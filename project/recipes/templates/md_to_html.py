"""Script for converting Markdown (*.md) files containing recipes into HTML template files."""
from dataclasses import dataclass, field
import markdown
import os


@dataclass
class Recipe:
    """Data structure representing a recipe."""
    input_filename: str
    output_filename: str
    title: str = ''
    description: list = field(default_factory=lambda: [])
    image: str = ''
    tips: list = field(default_factory=lambda: [])
    ingredients: list = field(default_factory=lambda: [])
    steps: list = field(default_factory=lambda: [])

    def parse_markdown_file(self):
        """Parses a Markdown file containing a recipe."""
        input_lines = []
        current_section = ''

        with open(self.input_filename, 'r') as f:
            input_lines = f.readlines()

        for line in input_lines:
            # print(f'line: {line}')
            if line.startswith('## '):
                # print(f"line.strip().lstrip('## '): *{line.strip('## ')}*")
                current_section = line.strip().lstrip('## ')
                # print(f'New current_section: {current_section}')
            else:
                if line.strip() == '':
                    continue

                if current_section == 'Title':
                    self.title = line.strip()
                elif current_section == 'Description':
                    self.description.append(line)
                elif current_section == 'Image':
                    self.image = line.strip()
                elif current_section == 'Tips':
                    self.tips.append(line)
                elif current_section == 'Ingredients':
                    self.ingredients.append(line.strip())
                elif current_section == 'Steps':
                    self.steps.append(line.strip())

    def print_to_console(self):
        """Prints the recipe to the console."""
        print(f'{self.title} Recipe:')
        print('---------------')
        print(f'Description: {self.description}')
        print(f'Image: {self.image}')
        print(f'Tips: {self.tips}')
        print(f'Ingredients: {self.ingredients}')
        print(f'Steps: {self.steps}')

    def write_html_to_file(self):
        """Writes the HTML output to the recipe file."""
        with open(self.output_filename, 'w') as f:
            f.write('{% extends "recipe.html" %}\n')
            f.write('\n')

            f.write('{% block recipe_title %}\n')
            f.write(f'<h1>{self.title}</h1>\n')
            f.write('{% endblock %}\n')
            f.write('\n')

            f.write('{% block recipe_description %}\n')
            f.write('<h2>Description</h2>\n')
            f.write(markdown.markdown('\n'.join(self.description)))
            f.write('\n{% endblock %}\n')
            f.write('\n')

            f.write('{% block recipe_image %}\n')
            f.write(f'{self.image}\n')
            f.write('{% endblock %}\n')
            f.write('\n')

            f.write('{% block recipe_tips %}\n')
            f.write('<h2>Tips</h2>\n')
            f.write(markdown.markdown('\n'.join(self.tips)))
            f.write('\n{% endblock %}\n')
            f.write('\n')

            f.write('{% block recipe_ingredients %}\n')
            f.write('<h2>List of Ingredients</h2>\n')
            f.write(markdown.markdown('\n'.join(self.ingredients)))
            f.write('\n{% endblock %}\n')
            f.write('\n')

            f.write('{% block recipe_steps %}\n')
            f.write('<h2>Recipe Steps</h2>\n')
            f.write(markdown.markdown('\n'.join(self.steps)))
            f.write('\n{% endblock %}\n')


if __name__ == "__main__":
    for file in os.listdir(os.path.join('project', 'recipes', 'templates', 'markdown')):
        # For each Markdown file, convert it to an HTML file
        if file.endswith('.md'):
            filename, _ = os.path.splitext(file)
            recipe = Recipe(
                os.path.join(os.getcwd(), 'project', 'recipes', 'templates', 'markdown', file),
                os.path.join(os.getcwd(), 'project', 'recipes', 'templates', 'recipes', filename + '.html')
            )
            recipe.parse_markdown_file()
            recipe.write_html_to_file()
            print(f'Converted {file} into an HTML template file!')
