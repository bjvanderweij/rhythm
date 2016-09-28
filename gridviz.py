import svgwrite, argparse, sys
from functools import reduce
from operator import mul
from utils import grid_to_iois, iois_to_grid


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


def draw_metrical_grid(drawing, length, subdivisions, *, x_offset, y_offset, spacing, radius, color, stroke_width, phase=0):

    for position in range(length):

        for level in range(len(subdivisions)):

            period = reduce(mul, subdivisions[:level+1])

            if (position + phase) % period == 0:

                draw_grid_point(
                    drawing, 
                    x_offset=x_offset + position * spacing,
                    y_offset=y_offset + level * spacing,
                    radius=radius,
                    color=color,
                    fill_color=color,
                    fill_opacity=100,
                    stroke_width=stroke_width,
                )

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

    drawing.save()


