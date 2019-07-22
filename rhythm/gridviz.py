import svgwrite, argparse, sys
from functools import reduce
from operator import mul
from utils import grid_to_iois, iois_to_grid
import os


def draw_grid_point(drawing, *, x_offset, y_offset, radius, color, stroke_width=2, fill_color='#ffffff', fill_opacity=0):

    drawing.add(svgwrite.shapes.Circle(
        center=(x_offset, y_offset),
        style='fill: %s; fill-opacity:%d; stroke-width: %d; stroke: %s' % (
            fill_color, 
            fill_opacity, 
            stroke_width, 
            color
        ),
        r=radius,
    ))

def draw_onset_grid(drawing, grid, *, x_offset, y_offset, spacing, radius, color, stroke_width):

    # Draw equidistant circles for each position in the grid
    for position, onset in enumerate(grid):

        fill_opacity = 0

        if onset == 1:
            fill_opacity = 100

        draw_grid_point(
            drawing, 
            x_offset=x_offset + position * spacing,
            y_offset=y_offset,
            radius=radius,
            color=color,
            fill_color=color,
            fill_opacity=fill_opacity,
            stroke_width=stroke_width,
        )

    return drawing


def draw_metrical_grid(drawing, length, subdivisions, *, x_offset, y_offset, spacing, radius, color, stroke_width, phase=0, flip=False):

    for position in range(length):

        for level in range(len(subdivisions)):

            period = reduce(mul, subdivisions[:level+1])

            if (position + phase) % period == 0:

                draw_grid_point(
                    drawing, 
                    x_offset=x_offset + position * spacing,
                    y_offset=y_offset + (-1 if flip else 1) * level * spacing,
                    radius=radius,
                    color=color,
                    fill_color=color,
                    fill_opacity=100,
                    stroke_width=stroke_width,
                )

    return drawing

def draw_grid(grid, output_file, foregroud_color='000000', subdivisions=[], phase=0):

    spacing = 50
    stroke_width = 2
    radius = 10

    size = ('%d' % (2 * radius + len(grid) * spacing + spacing),
            '%d' % (2 * radius + (2 + len(args.subdivisions)) * spacing))
    drawing = svgwrite.Drawing(filename=args.output_file, profile='basic', size=size)

    drawing = draw_onset_grid(drawing, grid, 
            x_offset=spacing, 
            y_offset=spacing, 
            color='#%s' % args.foreground_color, 
            spacing=spacing,
            stroke_width=stroke_width,
            radius=radius,)
    if len(args.subdivisions) > 0:
        drawing = draw_metrical_grid(drawing, len(grid), [1] + args.subdivisions, phase=args.phase,
                x_offset=spacing, 
                y_offset=2 * spacing, 
                color='#c8c8c8', 
                spacing=spacing,
                stroke_width=stroke_width,
                radius=radius,)

    return drawing

if __name__ == '__main__':

    solarized_fg = '657b83'

    parser = argparse.ArgumentParser(description=
            'Visualise an input rhythm as a grid of shaded and unshaded nodes.')
    parser.add_argument('rhythm', nargs='*', default=None)
    parser.add_argument('-i', '--input-format', default='grid', help='format of the input rhythms')
    parser.add_argument('-c', '--foreground-color', default='000000', help='foreground color')
    parser.add_argument('-o', '--output-file', default='grid.svg', help='Provide an output file.')
    parser.add_argument('-s', '--subdivisions', type=int, default=[], nargs='+', )
    parser.add_argument('-p', '--phase', type=int, default=0)
    args = parser.parse_args()

    grid = []
    if args.input_format == 'grid':
        grid = [int(p) for p in args.rhythm]
    elif args.input_format == 'ioi':
        offset, *iois = (int(p) for p in args.rhythm)
        grid = iois_to_grid(offset, tuple(iois))
    else:
        print('unrecognised input format')

    drawing = draw_grid(drawing, grid, args.output_file, **vars(args))
    drawing.save()

def frontiers():

    congruent = list(map(lambda r: iois_to_grid(0, r), (
        (6, 2, 2, 2), 
        (8, 2, 2), 
        (3, 1, 2, 1, 2, 1, 1), )))

    incongruent = list(map(lambda r: iois_to_grid(0, r), (
        (6, 2, 2, 2), 
        (8, 2, 2), 
        (3, 1, 2, 1, 2, 1, 1), )))

    simple = [2, 3, 2]
    compound = [2, 2, 3]

    root_path = '/home/bastiaan/projects/phd/work/papers/frontiers-musinf/illustrations'

    def save_rhythms(base_name, rhythms):

        filenames = ('%s-%s.svg' % (basename, i) for i in range(len(rhythms)))
        paths = map(lambda filename: os.path.join(root_path, filename), filenames)

        for rhythm, f in zip(rhythms, paths):
            drawing = draw_double_grid(rhythm, f, subdivisions_1=simple, subdivisions_2=compound)
            drawing.save()

    save_rhythms('congruent', congruent)
    save_rhythms('incongruent', incongruent)

def draw_double_grid(grid, output_file, foreground_color='000000', subdivisions_1=[], subdivisions_2=[], phase=0, highlight=[]):

    spacing = 50
    stroke_width = 0
    radius = 10
    grid_color = '#c8c8c8'
    highlight_color = '#e0e0e0'
    
    grid_height = lambda subdivisions: (1 + len(subdivisions)) * spacing

    size = ('%d' % (spacing + len(grid) * spacing),
            '%d' % (2 * spacing + grid_height(subdivisions_1) + grid_height(subdivisions_2)))

    drawing = svgwrite.Drawing(filename=output_file, profile='basic', size=size)

    for position in highlight:

        x_offset = spacing + position * spacing - (0.9 * 0.5 * spacing)
        y_offset = spacing - (0.9 * 0.5 * spacing)
        width = (0.9 * 0.5 * spacing) * 2 
        height = (0.9 * 0.5 * spacing) * 2 + grid_height(subdivisions_1) + grid_height(subdivisions_2)

        drawing.add(svgwrite.shapes.Rect(
            insert=(x_offset, y_offset),
            size=(width, height),
            rx=radius, ry=radius,
            style='fill: %s; fill-opacity:%d; stroke-width: %d; stroke: %s' % (
                highlight_color, 1, stroke_width, highlight_color
            ),
        ))

    drawing = draw_onset_grid(drawing, grid, 
            x_offset=spacing, 
            y_offset=grid_height(subdivisions_1) + 1 * spacing, 
            color='#%s' % foreground_color, 
            spacing=spacing,
            stroke_width=stroke_width,
            radius=radius,)
    drawing = draw_metrical_grid(drawing, len(grid), [1] + subdivisions_1, phase=phase,
            x_offset=spacing, 
            y_offset=grid_height(subdivisions_1),
            color=grid_color, 
            spacing=spacing,
            stroke_width=stroke_width,
            radius=radius,
            flip=True)
    drawing = draw_metrical_grid(drawing, len(grid), [1] + subdivisions_2, phase=phase,
            x_offset=spacing, 
            y_offset=2 * spacing + grid_height(subdivisions_1), 
            color=grid_color, 
            spacing=spacing,
            stroke_width=stroke_width,
            radius=radius,)

    return drawing



