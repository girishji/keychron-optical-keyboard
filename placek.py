# Copyright (C) 2022 Girish Palya <girishji@gmail.com>
# License: https://opensource.org/licenses/MIT
#
# Console script to place footprints
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
from pcbnew import wxPoint, wxPointMM
import itertools
import math


class Switch:
    # S, RL
    _pos = {
        "S": (0, 0),
        "RL": (8.3, -1.5),
    }

    _radius = 1.5 * 1e6

    def __init__(self, board, num) -> None:
        if not board and not num:
            return  # dummy
        self.footprints = {
            "S": board.FindFootprintByReference("S" + str(num)),
            "RL": board.FindFootprintByReference("RL" + str(num)),
        }
        self.orient()

    def orient(self):
        orientation = {"S": 0, "RL": -90}
        for sym, fp in self.footprints.items():
            if fp:
                fp.SetOrientation(orientation[sym] * 10)

    def get_pad_center(self, fp, pad_num):
        return self.footprints[fp].FindPadByNumber(str(pad_num)).GetCenter()

    def add_tracks(self):
        sta = self.get_pad_center("RL", 2)
        end = self.get_pad_center("S", 1)
        end1 = wxPoint(sta.x, end.y - Switch._radius)
        add_track(sta, end1)
        end2 = add_arc_from(end1, 0, 1, 0, 0)
        add_track(end2, end)

    def place(self, offset):
        for fp in self._pos.keys():
            if self.footprints[fp]:
                p = wxPointMM(
                    Switch._pos[fp][0] + offset[0], Switch._pos[fp][1] + offset[1]
                )
                self.footprints[fp].SetPosition(p)

    def place_fp(self, fp, offset, orient):
        if fp:
            pos = self.footprints["S"].GetPosition()
            fp_pos = wxPoint(pos[0] + offset[0] * 1e6, pos[1] + offset[1] * 1e6)
            fp.SetPosition(fp_pos)
            fp.SetOrientation(orient * 10)  # 1/10 of degree

    def rotate(self, deg):
        p = self.footprints["S"].GetPosition()
        for _, fp in self.footprints.items():
            if fp:
                fp.Rotate(p, deg * 10)


class Keyboard(object):
    DIM = 19.00
    RADIUS = 3 * pcbnew.IU_PER_MM

    def __init__(self) -> None:
        self.switches = [Switch(None, None)]
        board = pcbnew.GetBoard()
        for i in range(1, 75):
            self.switches.append(Switch(board, i))
        self.RP = [
            board.FindFootprintByReference("RP" + str(fp))
            for fp in [1] + list(range(1, 16))
        ]

    def place_footprints(self):
        dim = Keyboard.DIM
        board = pcbnew.GetBoard()
        rp_pos = (-8.3, -7.4)

        # row 1
        for i in range(1, 16):
            self.switches[i].place((i * dim, 0))
        self.switches[30].place((16 * dim - dim / 2, 0))

        # row 2
        offs = dim + dim / 4
        self.switches[16].place((offs, dim))
        for i in range(17, 29):
            self.switches[i].place((offs + dim / 4 + (i - 16) * dim, dim))
        self.switches[29].place((offs + dim / 4 + dim * 13 + dim / 4, dim))

        # row 3
        self.switches[30].place((dim / 2 + dim / 4, 2 * dim))
        self.switches[31].place((3 * dim / 2 + dim / 4, 2 * dim))
        offs = 3 * dim / 2 + dim / 4
        for i in range(32, 43):
            self.switches[i].place((offs + (i - 31) * dim, 2 * dim))
        offs += 12 * dim + dim / 8
        self.switches[43].place((offs, 2 * dim))
        self.switches[44].place((offs + dim + dim / 8, 2 * dim))

        # row 4
        offs = dim * (0.5 + 0.75 / 2)
        self.switches[45].place((offs + dim / 4, 3 * dim))
        offs += dim + dim * 0.75 / 2
        for i in range(46, 57):
            self.switches[i].place((offs + (i - 46) * dim, 3 * dim))
        offs += dim * 11
        self.switches[57].place((offs + dim / 8, 3 * dim))
        offs += dim * 1.25
        self.switches[58].place((offs, 3 * dim))
        self.switches[59].place((offs + dim, 3 * dim))
        for i in range(1, 16):
            self.switches[i + 44].place_fp(self.RP[i], rp_pos, 90)

        # row 5
        for i in range(60, 63):
            self.switches[i].place((dim / 2 + (i - 60) * dim + dim / 4, 4 * dim))
        offs = dim / 2 + dim * 3
        self.switches[63].place((offs + dim / 4, 4 * dim))

        # self.switches[64].place((offs + dim * 1.25 + dim / 8, 4 * dim))
        self.switches[64].place((offs + dim * 1.25 + dim / 8 + 1.4, 4 * dim + 5))
        self.switches[64].rotate(-16)
        offs += dim * 1.25 * 2
        # self.switches[65].place((offs - 1.5, 4.5 * dim + 4))
        self.switches[65].place((offs - 1.0, 4.5 * dim + 7))
        # self.switches[66].rotate(-15 + 90)
        self.switches[65].rotate(-20 + 90)

        offs += dim * 1.25
        self.switches[66].place((offs, 4 * dim))

        # self.switches[67].place((offs + dim + dim / 4 + 1.5, 4.5 * dim + 4))
        self.switches[67].place((offs + dim + dim / 4 + 1.0, 4.5 * dim + 7))
        self.switches[67].rotate(20 + 90)
        offs += dim * 1.25
        # self.switches[68].place((offs + dim, 4 * dim))
        self.switches[68].place((offs + dim - 1.4, 4 * dim + 5))
        self.switches[68].rotate(16)
        offs += dim

        for i in range(69, 75):
            self.switches[i].place((offs + (i - 68) * dim, 4 * dim))

        bp = board.FindFootprintByReference("U1")
        if bp:
            bp.SetOrientation(0 * 10)
            bp.SetPosition(wxPointMM(-dim / 4 - 1.5, 3 * dim - 2.0))

        led = board.FindFootprintByReference("D1")
        ledR = board.FindFootprintByReference("R1")
        self.switches[50].place_fp(led, (0, -4.8), 0)
        self.switches[50].place_fp(ledR, (8.3, 5), 90)

        pcbnew.Refresh()

    def remove_tracks(self):
        # delete tracks and vias
        board = pcbnew.GetBoard()
        for t in board.GetTracks():
            board.Delete(t)

    def add_via(self, loc):
        board = pcbnew.GetBoard()
        via = pcbnew.PCB_VIA(board)
        via.SetPosition(loc)
        # via.SetDrill(int(0.3 * 1e6))
        # via.SetWidth(int(0.6 * 1e6))
        via.SetDrill(int(0.4 * 1e6))
        via.SetWidth(int(0.8 * 1e6))
        board.Add(via)

    def via_track(self, point, offset=-1.0, reverse=False, vertical=False):
        offset = -offset if reverse else offset
        end = (
            wxPoint(point.x + offset * 1e6, point.y)
            if not vertical
            else wxPoint(point.x, point.y + offset * 1e6)
        )
        add_track(point, end)
        self.add_via(end)
        return end

    def add_tracks(self):
        # add tracks
        for i in range(1, 75):
            if i not in (64, 65, 67, 68):
                self.switches[i].add_tracks()

        # rows
        for i in itertools.chain(
            range(1, 15),
            range(16, 29),
            range(30, 44),
            range(45, 59),
            range(60, 64),
            range(69, 74),
        ):
            sw1 = self.switches[i]
            sw2 = self.switches[i + 1]
            start = sw1.get_pad_center("RL", 1)
            end = sw2.get_pad_center("RL", 1)
            add_track(start, end)

        for i in range(1, 15):
            sta = self.RP[i].FindPadByNumber(str(2)).GetCenter()
            end = self.RP[i + 1].FindPadByNumber(str(2)).GetCenter()
            add_track(sta, end)

        # columns
        up, down = {}, {}
        for i in range(1, 75):
            sta = self.switches[i].get_pad_center("S", 3)
            offset = -1 if i not in (73, 74, 66) else -1 - Switch._radius / 1e6
            sta1 = self.via_track(sta, offset=offset)
            if i in range(1, 16):
                sta2 = add_arc_from(sta1, 0, 1, 1, 1, True, layer=pcbnew.B_Cu)
                down[i] = wxPoint(sta2.x, sta2.y + Switch._radius)
                add_track(sta2, down[i], layer=pcbnew.B_Cu)
            elif i in (64, 65, 67, 68):
                continue
            elif i >= 60:
                up[i] = add_arc_from(sta1, 0, 0, 1, 0, layer=pcbnew.B_Cu)
            else:
                end1 = add_arc_from(sta1, 0, 0, 0, 1, True, layer=pcbnew.B_Cu)
                up[i] = add_arc_from(end1, 0, 0, 1, 0, layer=pcbnew.B_Cu)
                end1 = add_arc_from(sta1, 0, 1, 0, 0, layer=pcbnew.B_Cu)
                down[i] = add_arc_from(end1, 0, 1, 1, 1, True, layer=pcbnew.B_Cu)

        exclude = (64, 65, 67, 68, -1)
        for i1, i2, i3, i4, i5 in list(
            zip(
                range(1, 15),
                range(16, 30),
                range(30, 44),
                range(45, 59),
                range(60, 74),
            )
        ) + [(-1, -1, 44, 59, 74)]:
            for st, en in [(i1, i2), (i2, i3), (i3, i4), (i4, i5)]:
                if st in exclude or en in exclude:
                    continue
                sta, end = down[st], up[en]
                sta1 = sta
                end1 = wxPoint(end.x, sta1.y + 2 * Switch._radius)
                add_track(end, end1, layer=pcbnew.B_Cu)
                if sta1.x < end1.x:
                    sta2 = add_arc_from(sta1, 1, 1, 1, 0, True, layer=pcbnew.B_Cu)
                    end2 = add_arc_from(end1, 0, 0, 0, 1, True, layer=pcbnew.B_Cu)
                    add_track(sta2, end2, layer=pcbnew.B_Cu)
                elif sta1.x > end1.x:
                    sta2 = add_arc_from(sta1, 0, 1, 0, 0, layer=pcbnew.B_Cu)
                    end2 = add_arc_from(end1, 1, 0, 1, 1, layer=pcbnew.B_Cu)
                    add_track(sta2, end2, layer=pcbnew.B_Cu)
                else:
                    add_track(sta1, end1, layer=pcbnew.B_Cu)

        # ground
        for i in range(1, 75):
            if i not in (64, 65, 67, 68):
                self.via_track(self.switches[i].get_pad_center("S", 2), offset=1.0)
                self.via_track(self.switches[i].get_pad_center("S", 4), offset=-1.0)

        pcbnew.Refresh()


def add_track(start, end, layer=pcbnew.F_Cu):
    board = pcbnew.GetBoard()
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(start)
    track.SetEnd(end)
    track.SetWidth(int(0.25 * 1e6))
    track.SetLayer(layer)
    board.Add(track)


def add_arc(start, end, mid, layer=pcbnew.F_Cu):
    board = pcbnew.GetBoard()
    track = pcbnew.PCB_ARC(board)
    track.SetStart(start)
    track.SetEnd(end)
    track.SetMid(mid)
    if track.GetAngle() < 0:
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(start)
        track.SetEnd(end)
    track.SetWidth(int(0.25 * 1e6))
    track.SetLayer(layer)
    board.Add(track)


def add_arc_from(
    point, ex, ey, mx, my, reverse=False, d=Switch._radius, layer=pcbnew.F_Cu
):
    end = wxPoint(point.x + (d if ex else -d), point.y + (d if ey else -d))
    mid = wxPoint(point.x + (d if mx else -d), point.y + (d if my else -d))
    if reverse:
        add_arc(end, point, mid, layer)
    else:
        add_arc(point, end, mid, layer)
    return end


def transform(pt, around, theta):
    matrix = [
        [math.cos(math.radians(theta)), -math.sin(math.radians(theta))],
        [math.sin(math.radians(theta)), math.cos(math.radians(theta))],
    ]
    return wxPoint(
        around.x + pt.x * matrix[0][0] + pt.y * matrix[0][1],
        around.y + pt.x * matrix[1][0] + pt.y * matrix[1][1],
    )


kb = Keyboard()
kb.place_footprints()
kb.remove_tracks()
kb.add_tracks()
