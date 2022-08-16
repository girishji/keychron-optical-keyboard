# Copyright (C) 2022 Girish Palya <girishji@gmail.com>
# License: https://opensource.org/licenses/MIT
#
# Console script to place mouting holes
#
# To run as script in python console,
#   place or symplink this script to ~/Documents/KiCad/6.0/scripting/plugins
#   Run from python console using 'import filename'
#   To reapply:
#     import importlib
#     importlib.reload(filename)
#  OR
#    exec(open("path-to-script-file").read())

import pcbnew
from pcbnew import wxPoint
import math


DIM = 19.0 * pcbnew.IU_PER_MM
RADIUS = 3.0 * pcbnew.IU_PER_MM
BORDER = 4.0 * pcbnew.IU_PER_MM
HOLE_OFFSET = 1.0 * pcbnew.IU_PER_MM

WR = {
    "offset": 64 * pcbnew.IU_PER_MM,
    "depth": 87 * pcbnew.IU_PER_MM,
    "standoff": 28 * pcbnew.IU_PER_MM,
}

SWITCHES = [pcbnew.GetBoard().FindFootprintByReference("S1")]  # dummy
for i in range(1, 75):
    SWITCHES.append(pcbnew.GetBoard().FindFootprintByReference("S" + str(i)))


def add_line(start, end, layer=pcbnew.Edge_Cuts):
    board = pcbnew.GetBoard()
    ls = pcbnew.PCB_SHAPE(board)
    ls.SetShape(pcbnew.SHAPE_T_SEGMENT)
    ls.SetStart(start)
    ls.SetEnd(end)
    ls.SetLayer(layer)
    # ls.SetWidth(int(0.1 * pcbnew.IU_PER_MM))
    board.Add(ls)


def add_line_arc(start, center, reverse=False, angle=-90, layer=pcbnew.Edge_Cuts):
    board = pcbnew.GetBoard()
    arc = pcbnew.PCB_SHAPE(board)
    arc.SetShape(pcbnew.SHAPE_T_ARC)
    arc.SetStart(start)
    arc.SetCenter(center)
    arc.SetArcAngleAndEnd(-angle * 10, reverse)
    arc.SetLayer(layer)
    # arc.SetWidth(int(0.1 * pcbnew.IU_PER_MM))
    board.Add(arc)


def centerpt(start, quadrant, d=RADIUS):
    ctr = {
        1: wxPoint(start.x + d, start.y),
        2: wxPoint(start.x, start.y + d),
        3: wxPoint(start.x - d, start.y),
        4: wxPoint(start.x, start.y - d),
    }
    return ctr[quadrant]


def endpt(start, quadrant, d=RADIUS):
    end = {
        1: wxPoint(start.x + d, start.y + d),
        2: wxPoint(start.x - d, start.y + d),
        3: wxPoint(start.x - d, start.y - d),
        4: wxPoint(start.x + d, start.y - d),
    }
    return end[quadrant]


def transform(pt, around, theta):
    matrix = [
        [math.cos(math.radians(theta)), -math.sin(math.radians(theta))],
        [math.sin(math.radians(theta)), math.cos(math.radians(theta))],
    ]
    return wxPoint(
        around.x + pt.x * matrix[0][0] + pt.y * matrix[0][1],
        around.y + pt.x * matrix[1][0] + pt.y * matrix[1][1],
    )


def remove_drawings():
    board = pcbnew.GetBoard()
    for t in board.GetDrawings():
        board.Delete(t)


def draw_border_tilted_keys():
    dim = DIM
    brd = BORDER
    rad = RADIUS
    board = pcbnew.GetBoard()
    switches = SWITCHES

    sw = switches[63].GetPosition()
    degl = -switches[63].GetOrientation() // 10
    lsta = wxPoint(-dim / 2 - dim / 8, dim / 2 + brd)
    lend = wxPoint(0, dim / 2 + brd)
    sta = transform(lsta, sw, degl)
    end = transform(lend, sw, degl)
    add_line(sta, end)

    sw = switches[64].GetPosition()
    deg = 90 - switches[64].GetOrientation() // 10
    lsta = wxPoint(-dim / 2 - brd + rad, dim / 2 + dim / 8 + brd)
    lend = wxPoint(dim / 2 + brd - rad, dim / 2 + dim / 8 + brd)
    sta = transform(lsta, sw, deg)
    end = transform(lend, sw, deg)
    add_line(sta, end)
    ctr = transform(wxPoint(lsta.x, lsta.y - rad), sw, deg)
    add_line_arc(sta, ctr)
    end1 = transform(wxPoint(lsta.x - rad, lsta.y - rad), sw, deg)
    lend2 = wxPoint(lsta.x - rad, lsta.y - dim / 2 + 5.5 * pcbnew.IU_PER_MM)
    end2 = transform(lend2, sw, deg)
    add_line(end1, end2)
    ctr = transform(wxPoint(lend2.x - rad, lend2.y), sw, deg)
    add_line_arc(end2, ctr, reverse=True, angle=90 + deg - degl)
    ctr = transform(wxPoint(lend.x, lend.y - rad), sw, deg)
    add_line_arc(end, ctr, reverse=True, angle=90)
    lend1 = wxPoint(lend.x + rad, lend.y - rad)
    end1 = transform(lend1, sw, deg)
    lend2 = wxPoint(lend1.x, lend1.y - dim + 1 * pcbnew.IU_PER_MM)
    end2 = transform(lend2, sw, deg)
    add_line(end1, end2)
    ctr = transform(wxPoint(lend2.x + rad, lend2.y), sw, deg)
    add_line_arc(end2, ctr, reverse=False, angle=-90 + deg)

    sw = switches[67].GetPosition()
    degr = -switches[67].GetOrientation() // 10
    lsta = wxPoint(0, dim / 2 + brd)
    lend = wxPoint(dim / 2, dim / 2 + brd)
    sta = transform(lsta, sw, degr)
    end = transform(lend, sw, degr)
    add_line(sta, end)

    sw = switches[66].GetPosition()
    deg = 90 - switches[66].GetOrientation() // 10
    lend = wxPoint(-dim / 2 - brd + rad, dim / 2 + dim / 8 + brd)
    lsta = wxPoint(dim / 2 + brd - rad, dim / 2 + dim / 8 + brd)
    sta = transform(lsta, sw, deg)
    end = transform(lend, sw, deg)
    add_line(sta, end)
    ctr = transform(wxPoint(lsta.x, lsta.y - rad), sw, deg)
    add_line_arc(sta, ctr, reverse=True, angle=90)
    end1 = transform(wxPoint(lsta.x + rad, lsta.y - rad), sw, deg)
    lend2 = wxPoint(lsta.x + rad, lsta.y - dim / 2 + 5.0 * pcbnew.IU_PER_MM)
    end2 = transform(lend2, sw, deg)
    add_line(end1, end2)
    ctr = transform(wxPoint(lend2.x + rad, lend2.y), sw, deg)
    add_line_arc(end2, ctr, reverse=False, angle=-90 + deg - degr)
    ctr = transform(wxPoint(lend.x, lend.y - rad), sw, deg)
    add_line_arc(end, ctr, reverse=False, angle=-90)
    lend1 = wxPoint(lend.x - rad, lend.y - rad)
    end1 = transform(lend1, sw, deg)
    lend2 = wxPoint(lend1.x, lend1.y - dim + 1 * pcbnew.IU_PER_MM)
    end2 = transform(lend2, sw, deg)
    add_line(end1, end2)
    ctr = transform(wxPoint(lend2.x - rad, lend2.y), sw, deg)
    add_line_arc(end2, ctr, reverse=True, angle=90 + deg)


def draw_support(start):
    ho = HOLE_OFFSET
    rad = RADIUS
    dim = DIM
    brd = BORDER
    switches = SWITCHES

    def place_hole(center):
        hole = pcbnew.GetBoard().FindFootprintByReference(
            "HS" + str(draw_support.holenum)
        )
        draw_support.holenum += 1
        if hole:
            hole.SetPosition(center)

    end = wxPoint(start.x, start.y + rad)
    add_line(start, end)
    sta = sleft = end
    end = wxPoint(sta.x, sta.y + WR["depth"] - WR["standoff"] - 2 * rad)
    add_line(sta, end)
    place_hole(wxPoint(end.x + rad + ho, end.y - ho))
    add_line_arc(end, centerpt(end, 1), reverse=True, angle=90)
    sta = endpt(end, 1)
    if not draw_support.width:
        ctr = switches[65].GetPosition()
        draw_support.width = ctr.x - WR["offset"] - sta.x + rad
        print(draw_support.width)
    elif switches[44]:
        redge = switches[44].GetPosition()
        draw_support.width = redge.x + dim / 2 - sta.x + brd + rad
        print(draw_support.width)
    end = wxPoint(sta.x + draw_support.width - 2 * rad, sta.y)
    add_line(sta, end)
    add_line_arc(end, centerpt(end, 4), reverse=True, angle=90)
    sta = endpt(end, 4)
    place_hole(wxPoint(end.x - ho, end.y - rad - ho))
    end = wxPoint(sta.x, sta.y - WR["depth"] + WR["standoff"] + 2 * rad)
    add_line(sta, end)
    sright = end
    endrt = wxPoint(end.x, end.y - rad)
    add_line(end, endrt)

    # user.drawings lines
    def draw_standoff(sta, end):
        add_line(sta, end, layer=pcbnew.Dwgs_User)
        add_line_arc(
            sta, centerpt(sta, 2), reverse=True, angle=90, layer=pcbnew.Dwgs_User
        )
        add_line_arc(
            end, centerpt(end, 2), reverse=False, angle=-90, layer=pcbnew.Dwgs_User
        )

    sta = wxPoint(sleft.x + rad, start.y)
    place_hole(wxPoint(sta.x + ho, sta.y + rad + ho))
    end = wxPoint(sright.x - rad, start.y)
    place_hole(wxPoint(end.x - ho, end.y + rad + ho))
    draw_standoff(sta, end)
    return endrt


draw_support.width = 0
draw_support.holenum = 1


def draw_border():
    dim = DIM
    brd = BORDER
    rad = RADIUS
    switches = SWITCHES
    blackpill_wid = (21.0 + 0.5) * pcbnew.IU_PER_MM

    # wrist support
    if not switches[1]:
        draw_support(wxPoint(0, 0))
        pcbnew.Refresh()
        return

    left = switches[30].GetPosition()
    topr = switches[15].GetPosition()
    tl = wxPoint(left.x - dim / 2 + rad, topr.y - dim / 2 - brd)
    tr = wxPoint(topr.x + dim / 2 + brd - rad, topr.y - dim / 2 - brd)
    add_line(tl, tr)
    add_line_arc(tl, centerpt(tl, 2), reverse=True, angle=90)
    end = wxPoint(tl.x - rad, tl.y + 2 * dim - rad + brd)
    add_line(endpt(tl, 2), end)

    blackpill = pcbnew.GetBoard().FindFootprintByReference("U1")
    bl = switches[59].GetPosition()
    ctr = switches[65].GetPosition()

    sdeg = -switches[63].GetOrientation() // 10
    if blackpill:
        add_line_arc(end, centerpt(end, 3))
        sta = endpt(end, 2)
        end = wxPoint(sta.x + rad - blackpill_wid, sta.y)
        add_line(sta, end)
        end1 = wxPoint(end.x, bl.y + dim / 2 + WR["standoff"])
        add_line(end, end1)
        sta = draw_support(end1)
        end = wxPoint(sta.x, ctr.y + dim / 2 + brd + rad + 1 * 1e6)
        add_line(sta, end)
        add_line_arc(end, centerpt(end, 1), angle=-90 - sdeg)
    else:
        end1 = wxPoint(end.x, bl.y + dim / 2 + brd - rad)
        add_line(end, end1)
        add_line_arc(end1, centerpt(end1, 1), reverse=True, angle=90)
        end2 = endpt(end1, 1)
        end3 = wxPoint(end2.x - rad + dim * 3.5 + 2 * 1e6, end2.y)
        add_line(end2, end3)
        add_line_arc(end3, centerpt(end3, 2), reverse=False, angle=-sdeg)

    sdeg = switches[67].GetOrientation() // 10
    # rad2 = 2 * 1e6
    if blackpill:
        sta = wxPoint(ctr.x + WR["offset"], ctr.y + dim / 2 + brd + rad + 1 * 1e6)
        add_line_arc(sta, centerpt(sta, 3), reverse=True, angle=90 + sdeg)
        end1 = wxPoint(sta.x, sta.y + WR["standoff"] - brd - rad - 1 * 1e6)
        add_line(sta, end1)
        sta = draw_support(end1)
        end3 = sta
    else:
        sta = wxPoint(ctr.x + WR["offset"], ctr.y + dim / 2 + brd)
        add_line_arc(sta, centerpt(sta, 2), reverse=True, angle=sdeg)
        sw = switches[44].GetPosition()
        end = wxPoint(sw.x + dim / 2 + brd - rad, sta.y)
        add_line(sta, end)
        add_line_arc(end, centerpt(end, 4), reverse=True, angle=90)
        end3 = endpt(end, 4)

    draw_border_tilted_keys()
    tsw = switches[15].GetPosition()
    end4 = wxPoint(end3.x, tsw.y - dim / 2 - brd + rad)
    add_line(end3, end4)
    add_line_arc(end4, centerpt(end4, 3), reverse=True, angle=90)

    pcbnew.Refresh()


# 90500000
# draw_support.width = 96750000
remove_drawings()
draw_border()
