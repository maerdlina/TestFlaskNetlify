import time
import math

import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
from cvxopt import matrix, spmatrix
from cvxopt.cholmod import linsolve

from scipy.ndimage import binary_closing, binary_opening, label
from scipy.ndimage import zoom
from scipy.ndimage import gaussian_filter

matplotlib.use('TkAgg')
class Load:
    def __init__(self, nelx, nely, E, nu):
        self.nelx = nelx
        self.nely = nely
        self.E = E
        self.nu = nu
        self.dim = 2

    def node(self, elx, ely):
        return (self.nely + 1) * elx + ely

    def nodes(self, elx, ely):
        n1 = self.node(elx, ely)
        n2 = self.node(elx + 1, ely)
        n3 = self.node(elx + 1, ely + 1)
        n4 = self.node(elx, ely + 1)
        return n1, n2, n3, n4

    def edof(self):
        elx = np.repeat(range(self.nelx), self.nely).reshape((self.nelx * self.nely, 1))
        ely = np.tile(range(self.nely), self.nelx).reshape((self.nelx * self.nely, 1))
        n1, n2, n3, n4 = self.nodes(elx, ely)
        edof = np.array([self.dim*n1, self.dim*n1+1, self.dim*n2, self.dim*n2+1,
                         self.dim*n3, self.dim*n3+1, self.dim*n4, self.dim*n4+1])
        edof = edof.T[0]
        x_list = np.repeat(edof, 8)
        y_list = np.tile(edof, 8).flatten()
        return edof, x_list, y_list

    def lk(self, E, nu):
        k = np.array([1/2-nu/6, 1/8+nu/8, -1/4-nu/12, -1/8+3*nu/8,
                      -1/4+nu/12, -1/8-nu/8, nu/6, 1/8-3*nu/8])
        ke = E/(1-nu**2) * np.array([[k[0], k[1], k[2], k[3], k[4], k[5], k[6], k[7]],
                                     [k[1], k[0], k[7], k[6], k[5], k[4], k[3], k[2]],
                                     [k[2], k[7], k[0], k[5], k[6], k[3], k[4], k[1]],
                                     [k[3], k[6], k[5], k[0], k[7], k[2], k[1], k[4]],
                                     [k[4], k[5], k[6], k[7], k[0], k[1], k[2], k[3]],
                                     [k[5], k[4], k[3], k[2], k[1], k[0], k[7], k[6]],
                                     [k[6], k[3], k[4], k[1], k[2], k[7], k[0], k[5]],
                                     [k[7], k[2], k[1], k[4], k[3], k[6], k[5], k[0]]])
        return ke

    def force(self):
        return np.zeros(self.dim*(self.nely+1)*(self.nelx+1))

    def alldofs(self):
        return [a for a in range(self.dim*(self.nely+1)*(self.nelx+1))]

    def fixdofs(self):
        return []

    def freedofs(self):
        return list(set(self.alldofs()) - set(self.fixdofs()))


class Cantilever(Load):
    def __init__(self, nelx, nely, E, nu):
        super().__init__(nelx, nely, E, nu)
        if nely % 2 != 0:
            raise ValueError('Nely needs to be even in a cantilever beam.')

    def force(self):
        f = super().force()
        n1, n2, n3, n4 = self.nodes(int(self.nelx - 1), int(self.nely - 1))
        # print(n2)
        f[self.dim * n2 + 1] = -1
        return f

    def fixdofs(self):
        return ([x for x in range(0, self.dim*(self.nely+1))])


class FESolver:
    def displace(self, load, x, ke, penal):
        freedofs = np.array(load.freedofs())
        nely, nelx = x.shape
        f_free = load.force()[freedofs]
        k_free = self.gk_freedofs(load, x, ke, penal)
        u = np.zeros(load.dim*(nely+1)*(nelx+1))
        u[freedofs] = spsolve(k_free, f_free)
        return u

    def gk_freedofs(self, load, x, ke, penal):
        freedofs = np.array(load.freedofs())
        nelx = load.nelx
        nely = load.nely
        edof, x_list, y_list = load.edof()
        factor = x.T.reshape(nelx*nely, 1, 1) ** penal
        value_list = (np.tile(ke, (nelx*nely, 1, 1))*factor).flatten()
        dof = load.dim*(nelx+1)*(nely+1)
        k = coo_matrix((value_list, (y_list, x_list)), shape=(dof, dof)).tocsc()
        k = k[freedofs, :][:, freedofs]
        return k

class CvxFEA(FESolver):
    def displace(self, load, x, ke, penal):
        freedofs = np.array(load.freedofs())
        nely, nelx = x.shape
        f = load.force()
        Matrix_free = matrix(f[freedofs])
        k_free = self.gk_freedofs(load, x, ke, penal).tocoo()
        k_free = spmatrix(k_free.data, k_free.row, k_free.col)
        u = np.zeros(load.dim*(nely+1)*(nelx+1))
        linsolve(k_free, Matrix_free)
        u[freedofs] = np.array(Matrix_free)[:, 0]
        return u

class BESO2D:
    def __init__(self, load, fesolver):
        self.load = load
        self.fesolver = fesolver
        self.vol = 1
        self.change = 1
        x = np.ones((load.nely, load.nelx))
        self.x = x
        self.dc = np.zeros(x.shape)
        self.c = np.zeros(200)
        self.nely, self.nelx = x.shape

    def topology(self, volfrac, er, rmin, penal, Plotting, Saving, callback=None):
        print('Hello! BESO!\nVersion : 0.3\nAuthor : Alina\n')
        vol = self.vol
        itr = 0
        itr_his = []
        com_his = []
        vol_his = []

        if Plotting:
            plt.ion()  # Включаем интерактивный режим
            fig, ax = plt.subplots(figsize=(10, 5))  # Создаем окно для графиков
            self.img = ax.imshow(np.zeros((self.nely, self.nelx)), cmap=plt.cm.grey, vmin=0, vmax=1)
            plt.colorbar(self.img, label='Плотность материала')
            plt.title(f'Итерация {itr + 1}')
            plt.draw()
            plt.pause(0.1)  # Пауза для обновления графика

        while self.change > 0.0001:
            if callback:
                callback(itr, self.x)
            load = self.load
            vol = max(vol * (1 - er), volfrac)
            change = self.change

            if itr > 0:
                olddc = self.dc

            x = self.x
            ke = load.lk(load.E, load.nu)
            u = self.fesolver.displace(load, x, ke, penal)
            dc = self.dc
            c = self.c

            for ely in range(self.nely):
                for elx in range(self.nelx):
                    n1, n2, n3, n4 = load.nodes(elx, ely)
                    Ue = u[np.array([2 * n1, 2 * n1 + 1, 2 * n2, 2 * n2 + 1,
                                     2 * n3, 2 * n3 + 1, 2 * n4, 2 * n4 + 1])]
                    c[itr] += 0.5 * (x[ely, elx] ** penal) * np.dot(np.dot(Ue.T, ke), Ue)
                    dc[ely, elx] = 0.5 * (x[ely, elx] ** (penal - 1)) * np.dot(np.dot(Ue.T, ke), Ue)

            dc = self.filt(rmin, x, dc)

            if itr > 0:
                dc = (dc + olddc) / 2

            x = self.rem_add(vol, dc, x)

            if itr >= 9:
                change = abs(np.sum(c[itr - 9:itr - 5]) - np.sum(c[itr - 4:itr])) / np.sum(c[itr - 4:itr])

            itr_his.append(itr + 1)
            com_his.append(c[itr])
            vol_his.append(vol)

            if Plotting:
                self.Plot(x, itr, fig)  # Визуализация
                plt.pause(0.01)  # Пауза для плавного обновления

            self.Update(vol, x, dc, c, change)
            itr += 1

        # Постобработка результатов с адаптивными параметрами
        x = self.postprocess(x)

        if Saving:
            self.SaveFig_x(x)
            self.SaveFig_his(itr_his, com_his, vol_his)
        print('\nCongratulations! Here it is!')

    def postprocess(self, x):
        # Адаптивный размер kernel в зависимости от размера конструкции
        kernel_size = max(1, min(self.nelx, self.nely) // 50)  # Пример: kernel_size = 2 для 100x50
        kernel = np.ones((kernel_size, kernel_size))

        # Бинаризация
        x_binary = x > 0.5

        # Проверка на значимость элементов
        labeled, num_features = label(x_binary)
        for i in range(1, num_features + 1):
            component = labeled == i
            if np.sum(component) < 5:  # Удаляем только очень мелкие компоненты
                x_binary[component] = 0

        # Морфологические операции с адаптивным kernel
        x_processed = binary_closing(x_binary, structure=kernel)  # Закрытие
        x_processed = binary_opening(x_processed, structure=kernel)  # Открытие

        return x_processed.astype(float)  # Возвращаем обратно в формат float

    def filt(self, rmin, x, dc):
        nely, nelx = x.shape
        rminf = math.floor(rmin)
        dcf = np.zeros((nely, nelx))

        for i in range(nelx):
            for j in range(nely):
                sum_ = 0
                for k in range(max(i-rminf, 0), min(i+rminf+1, nelx)):
                    for l in range(max(j-rminf, 0), min(j+rminf+1, nely)):
                        fac = rmin - math.sqrt((i-k)**2+(j-l)**2)
                        sum_ += max(0, fac)
                        dcf[j,i] += max(0, fac)*dc[l,k]
                dcf[j,i] /= sum_
        return dcf

    def rem_add(self, vol, dc, x):
        nely, nelx = x.shape
        lo = np.min(dc)
        hi = np.max(dc)

        while ((hi - lo) / hi) > 1e-5:
            th = (lo + hi) / 2.0
            x = np.maximum(0.001 * np.ones(np.shape(x)), np.sign(dc - th))

            if (np.sum(x) - vol * (nelx * nely)) > 0:
                lo = th
            else:
                hi = th
        return x

    def Plot(self, x, itr, fig):
        # Увеличиваем разрешение и применяем сглаживание
        smoothed_x = zoom(x, 8, order=3)  # Увеличиваем разрешение в 8 раз с кубической интерполяцией
        smoothed_x = gaussian_filter(smoothed_x, sigma=2)  # Применяем фильтр Гаусса с большим sigma
        self.img.set_data(1 - smoothed_x)  # Обновляем данные на графике
        plt.title(f'Итерация {itr + 1}')
        fig.canvas.draw()
        fig.canvas.flush_events()

    def History(self, itr_his, com_his, vol_his):
        fig = plt.figure()
        host = fig.add_subplot(111)
        par1 = host.twinx()
        host.set_xlim(0, max(itr_his)+5)
        host.set_ylim(min(com_his)*0.85, max(com_his)*1.15)
        par1.set_ylim(min(vol_his)*0.85, 1)
        host.set_xlabel("Iteration")
        host.set_ylabel("Mean compliance (Nmm)")
        par1.set_ylabel("Volume fraction")
        color1 = plt.cm.viridis(0)
        color2 = plt.cm.viridis(0.5)
        p1, = host.plot(itr_his, com_his, 'o-', color=color1, markersize=5, label="Compliance")
        p2, = par1.plot(itr_his, vol_his, 'o-', color=color2, markersize=5, markerfacecolor='white', label="Volume")
        lns = [p1, p2]
        host.legend(handles=lns, loc='best')
        host.yaxis.label.set_color(p1.get_color())
        par1.yaxis.label.set_color(p2.get_color())
        plt.show()

    def Update(self, vol, x, dc, c, change):
        self.vol = vol
        self.x = x
        self.dc = dc
        self.c = c
        self.change = change

    def SaveFig_x(self, x):
        plt.figure(figsize=(10, 5))
        # Увеличиваем разрешение и применяем сглаживание для сохранения
        smoothed_x = zoom(1 - x, 8, order=3)  # Увеличиваем разрешение в 8 раз с кубической интерполяцией
        smoothed_x = gaussian_filter(smoothed_x, sigma=2)  # Применяем фильтр Гаусса
        plt.imshow(smoothed_x, cmap=plt.cm.grey)  # Отображаем сглаженные данные
        plt.xticks([])
        plt.yticks([])
        plt.savefig('Topology.png', dpi=600)  # Увеличиваем DPI

    def SaveFig_his(self, itr_his, com_his, vol_his):
        fig = plt.figure()
        host = fig.add_subplot(111)
        par1 = host.twinx()
        host.set_xlim(0, max(itr_his)+5)
        host.set_ylim(min(com_his)*0.85, max(com_his)*1.15)
        par1.set_ylim(min(vol_his)*0.85, 1)
        host.set_xlabel("Iteration")
        host.set_ylabel("Mean compliance (Nmm)")
        par1.set_ylabel("Volume fraction")
        color1 = plt.cm.viridis(0)
        color2 = plt.cm.viridis(0.5)
        p1, = host.plot(itr_his, com_his, 'o-', color=color1, markersize=5, label="Compliance")
        p2, = par1.plot(itr_his, vol_his, 'o-', color=color2, markersize=5, markerfacecolor='white', label="Volume")
        lns = [p1, p2]
        host.legend(handles=lns, loc='best')
        host.yaxis.label.set_color(p1.get_color())
        par1.yaxis.label.set_color(p2.get_color())
        plt.savefig('History.png', dpi=300)


if __name__ == "__main__":
    # Material properties
    E = 1
    nu = 0.3

    # Физические размеры балки
    physical_length = 100  # Длина балки
    physical_width = 50  # Ширина балки

    # Коэффициент уменьшения сетки
    mesh_factor = 1

    # Количество элементов
    nelx = int(physical_length / mesh_factor)
    nely = int(physical_width / mesh_factor)

    # Optimization parameters
    vol_frac = 0.6
    penal = 3
    # Новый параметр фильтра
    rmin = 3 / mesh_factor
    er = 0.02

    # Applying load
    load = Cantilever(nelx, nely, E, nu)

    # FEA solver
    fesolver = CvxFEA()

    # Whether to plot the images every iteration
    Plotting = True

    # Whether to save the final images
    Saving = True

    # BESO optimization
    optimization = BESO2D(load, fesolver)

    # Execute the data
    t = time.time()
    x = np.ones((nely, nelx))
    ke = load.lk(load.E, load.nu)
    u = fesolver.displace(load, x, ke, penal)

    # Topology optimization
    optimization.topology(vol_frac, er, rmin, penal, Plotting, Saving)

    # Масштабирование результатов
    scaled_x = zoom(x, mesh_factor, order=1)

    # Print the time cost
    print('Time cost: ', time.time() - t, 'seconds.')