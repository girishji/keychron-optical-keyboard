# Place footprints console script
#
# To run as script in python console,
#   place or symplink this script to ~/Documents/KiCad/6.0/scripting/plugins
#   Run from python console using 'import placefp'
#   To reapply:
#     import importlib
#     importlib.reload(placefp)
#  OR
#    exec(open("path-to-script-file").read())

import pcbnew
import math
import itertools


class Switch:
    # S, RL
    _pos = {
        "S": (0, 0),
        "RL": (8.3, -1),
    }

    def __init__(self, board, num) -> None:
        if not board and not num:
            return  # dummy
        self.footprints = {
            "S": board.FindFootprintByReference("S" + str(num)),
            "RL": board.FindFootprintByReference("RL" + str(num)),
        }
        self.orient()

    def orient(self):
        self.footprints["S"].SetOrientation(0)  # 1/10 of degree
        self.footprints["RL"].SetOrientation(-90 * 10)  # 1/10 of degree

    @staticmethod
    def add_track(start, end, layer=pcbnew.F_Cu):
        board = pcbnew.GetBoard()
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(start)
        track.SetEnd(end)
        track.SetWidth(int(0.3 * 1e6))
        track.SetLayer(layer)
        board.Add(track)

    def get_pad_point(self, fp, pad_num):
        return self.footprints[fp].FindPadByNumber(str(pad_num)).GetCenter()

    def get_track_end(self, fp, pad_num, dist, orient=0):
        start = self.get_pad_point(fp, pad_num)
        deg = self.footprints[fp].GetOrientation() // 10
        d = dist * 1e6  # mm
        deg = 90 + deg + orient
        return pcbnew.wxPoint(
            start.x + d * math.cos(math.radians(deg)),
            start.y - d * math.sin(math.radians(deg)),
        )

    def add_tracks(self):
        sta = self.get_pad_point("RL", 2)
        end = self.get_track_end("RL", 2, -8.5)
        Switch.add_track(sta, end)
        end2 = self.get_pad_point("S", 1)
        Switch.add_track(end, end2)

    def place(self, offset):
        for fp in self._pos.keys():
            p = pcbnew.wxPointMM(
                Switch._pos[fp][0] + offset[0], Switch._pos[fp][1] + offset[1]
            )
            self.footprints[fp].SetPosition(p)

    @staticmethod
    def place_fp(offset, fp, pos, orient):
        fp.SetOrientation(orient * 10)  # 1/10 of degree
        p = pcbnew.wxPointMM(pos[0] + offset[0], pos[1] + offset[1])
        fp.SetPosition(p)

    def rotate(self, deg):
        p = self.footprints["S"].GetPosition()
        for _, fp in self.footprints.items():
            fp.Rotate(p, deg * 10)


class Keyboard(object):
    DIM = 19.00

    def __init__(self) -> None:
        self.switches = [Switch(None, None)]
        board = pcbnew.GetBoard()
        for i in range(1, 76):
            self.switches.append(Switch(board, i))
        self.RP = [
            board.FindFootprintByReference("RP" + str(fp))
            for fp in [1] + list(range(1, 16))
        ]

    def place_footprints(self):
        dim = Keyboard.DIM
        board = pcbnew.GetBoard()
        # rp_pos = (8.3, -0.5)

        # row 1
        for i in range(1, 16):
            self.switches[i].place((i * dim - dim / 2, 0))
        # Switch.place_fp((4 * dim, 0), self.RP[1], rp_pos, 90)
        self.switches[30].place((16 * dim - dim / 2, 0))

        # row 2
        offs = dim + dim / 4
        self.switches[16].place((offs, dim))
        for i in range(17, 29):
            self.switches[i].place((offs + dim / 4 + (i - 16) * dim, dim))
        self.switches[29].place((offs + dim / 4 + dim * 13 + dim / 4, dim))
        # Switch.place_fp((offs + dim / 4 + 3 * dim, dim), self.RP[2], rp_pos, 90)

        # row 3
        self.switches[31].place((dim / 2, 2 * dim))
        self.switches[32].place((3 * dim / 2 + dim / 8, 2 * dim))
        offs = 3 * dim / 2 + dim / 4
        for i in range(33, 44):
            self.switches[i].place((offs + (i - 32) * dim, 2 * dim))
        # Switch.place_fp((offs + 2 * dim, 2 * dim), self.RP[3], rp_pos, 90)
        offs += 12 * dim + dim / 4 + dim / 8
        self.switches[44].place((offs, 2 * dim))
        self.switches[45].place((offs + dim + dim / 4 + dim / 8, 2 * dim))

        # row 4
        offs = dim * (0.5 + 0.75 / 2)
        self.switches[46].place((offs, 3 * dim))
        offs += dim + dim * 0.75 / 2
        for i in range(47, 58):
            self.switches[i].place((offs + (i - 47) * dim, 3 * dim))
        # Switch.place_fp((offs + 2 * dim, 3 * dim), self.RP[4], rp_pos, 90)
        offs += dim * 11
        self.switches[58].place((offs + dim / 8, 3 * dim))
        offs += dim * 1.25
        self.switches[59].place((offs, 3 * dim))
        self.switches[60].place((offs + dim, 3 * dim))

        # row 5
        for i in range(61, 64):
            self.switches[i].place((dim / 2 + (i - 61) * dim, 4 * dim))
        offs = dim / 2 + dim * 3
        self.switches[64].place((offs + dim / 8, 4 * dim))
        # Switch.place_fp((offs + dim / 8, 4 * dim), self.RP[5], rp_pos, 90)
        self.switches[65].place((offs + dim * 1.25 + dim / 8, 4 * dim))
        offs += dim * 1.25 * 2
        self.switches[66].place((offs, 4.5 * dim))
        self.switches[66].rotate(-15 + 90)
        offs += dim * 1.25
        self.switches[67].place((offs, 4 * dim))
        # self.switches[30].place((offs, 5 * dim))
        self.switches[68].place((offs + dim + dim / 4, 4.5 * dim))
        self.switches[68].rotate(15 + 90)
        offs += dim * 1.25
        for i in range(69, 76):
            self.switches[i].place((offs + (i - 68) * dim, 4 * dim))

        tp1 = board.FindFootprintByReference("TP1")
        tp2 = board.FindFootprintByReference("TP2")
        tp1.SetPosition(pcbnew.wxPointMM(dim * 6.0, dim * 3.7))
        tp2.SetPosition(pcbnew.wxPointMM(dim * 6.2, dim * 3.7))

        bp = board.FindFootprintByReference("U1")
        bp.SetOrientation(90 * 10)  # 1/10 of degree
        # bp.SetPosition(pcbnew.wxPointMM(dim * 1.29, dim))
        bp.SetPosition(pcbnew.wxPointMM(dim * 1.29, 1 * dim + 2.6))

        pcbnew.Refresh()

    def remove_tracks(self):
        # delete tracks and vias
        board = pcbnew.GetBoard()
        tracks = board.GetTracks()
        for t in tracks:
            board.Delete(t)

    def add_via(self, loc):
        board = pcbnew.GetBoard()
        via = pcbnew.PCB_VIA(board)
        via.SetPosition(loc)
        via.SetDrill(int(0.3 * 1e6))
        via.SetWidth(int(0.6 * 1e6))
        board.Add(via)

    def _via_track(self, sta, end):
        Switch.add_track(sta, end)
        self.add_via(end)
        return end

    def via_track(self, sw, fp, pad_num, offset=-1.7):
        sta = sw.get_pad_point(fp, pad_num)
        end = sw.get_track_end(fp, pad_num, offset)
        return self._via_track(sta, end)

    def add_tracks(self):
        # add tracks
        for i in range(1, 76):
            self.switches[i].add_tracks()

        # rows
        for i in itertools.chain(
            range(1, 15),
            range(16, 29),
            range(31, 45),
            range(46, 60),
            range(61, 65),
            range(69, 75),
        ):
            sw1 = self.switches[i]
            start = sw1.get_pad_point("Q", 1)
            d = 1.5 * 1e6  # mm
            end = pcbnew.wxPoint(start.x + d, start.y - d)
            Switch.add_track(start, end)

            sw2 = self.switches[i + 1]
            start = sw2.get_pad_point("Q", 1)
            end2 = pcbnew.wxPoint(start.x - d, start.y - d)
            Switch.add_track(start, end2)
            Switch.add_track(end, end2)

        # columns
        exclude = [1, 2, 16, 15, 30, 66, 68]
        for i1, i2, i3, i4, i5 in zip(
            range(1, 16),
            range(16, 31),
            range(31, 46),
            range(46, 61),
            range(61, 76),
        ):
            vias = {
                sw: self.via_track(self.switches[sw], "RL", 1)
                for sw in [i1, i2, i3, i4, i5]
                if sw not in exclude
            }
            for st, en in [(i1, i2), (i2, i3), (i3, i4), (i4, i5)]:
                if st in exclude or en in exclude:
                    continue
                sta = vias[st]
                end = pcbnew.wxPoint(sta.x, sta.y + 4 * 1e6)
                Switch.add_track(sta, end, pcbnew.B_Cu)
                sta = vias[en]
                end2 = pcbnew.wxPoint(sta.x, sta.y - 7 * 1e6)
                Switch.add_track(sta, end2, pcbnew.B_Cu)
                Switch.add_track(end, end2, pcbnew.B_Cu)

        # RPs
        vias = {}
        for rp in range(1, 6):
            start = self.RP[rp].FindPadByNumber(str(2)).GetCenter()
            d = 1.7 * 1e6
            end = pcbnew.wxPoint(start.x + d, start.y)
            vias[rp] = self._via_track(start, end)
        for st, en in zip(range(1, 5), range(2, 6)):
            sta = vias[st]
            end = pcbnew.wxPoint(sta.x, sta.y + 9 * 1e6)
            Switch.add_track(sta, end, pcbnew.B_Cu)
            sta = vias[en]
            end2 = pcbnew.wxPoint(sta.x, sta.y - 2 * 1e6)
            Switch.add_track(sta, end2, pcbnew.B_Cu)
            Switch.add_track(end, end2, pcbnew.B_Cu)

        # ground
        for i in range(1, 76):
            sta = self.switches[i].get_pad_point("Q", 2)
            end = self.switches[i].get_track_end("Q", 2, -1.5)
            Switch.add_track(sta, end)
            self.add_via(end)
            sta = self.switches[i].get_pad_point("D", 1)
            end = self.switches[i].get_track_end("D", 1, -1.5)
            Switch.add_track(sta, end)
            self.add_via(end)

        pcbnew.Refresh()

    def add_holes(self):
        dim = Keyboard.DIM
        board = pcbnew.GetBoard()
        holes = [board.FindFootprintByReference("H1")]  # dummy
        holes += [
            board.FindFootprintByReference("H" + str(num)) for num in range(1, 21)
        ]
        holes[1].SetPosition(pcbnew.wxPointMM(dim * 3, dim * 0.5))
        holes[2].SetPosition(pcbnew.wxPointMM(dim * 4, dim * 1.5))
        holes[3].SetPosition(pcbnew.wxPointMM(dim * (1 + 1 / 8), dim * 2.0))
        holes[4].SetPosition(pcbnew.wxPointMM(dim * (1 / 4 + 1 / 8), dim * 3.0))
        holes[5].SetPosition(pcbnew.wxPointMM(dim * (2 + 1 / 2 + 1 / 4), dim * 3.5))
        holes[6].SetPosition(pcbnew.wxPointMM(dim * (4 + 3 / 4), dim * 2.5))
        holes[7].SetPosition(pcbnew.wxPointMM(dim * (6 + 3 / 4), dim * 2.5))
        holes[8].SetPosition(
            pcbnew.wxPointMM(dim * (5 + 3 / 4 - 1 / 8), dim * (3 + 1 / 2 + 1 / 8))
        )
        holes[9].SetPosition(
            pcbnew.wxPointMM(dim * (8 + 3 / 4 + 1 / 8), dim * (3 + 1 / 2 + 1 / 8))
        )
        holes[10].SetPosition(pcbnew.wxPointMM(dim * 8, dim * 0.5))
        holes[11].SetPosition(pcbnew.wxPointMM(dim * 10, dim * 1.5))
        holes[12].SetPosition(pcbnew.wxPointMM(dim * 12, dim * 1.5))
        holes[13].SetPosition(
            pcbnew.wxPointMM(dim * (14 + 1 / 8), dim * (1 / 2 + 1 / 8))
        )
        holes[14].SetPosition(pcbnew.wxPointMM(dim * (14 + 1 / 2 + 1 / 4), dim * (2)))
        holes[15].SetPosition(pcbnew.wxPointMM(dim * (12), dim * (3 + 1 / 2)))
        holes[16].SetPosition(pcbnew.wxPointMM(dim * (14), dim * (3 + 1 / 2 - 1 / 8)))

        holes[17].SetPosition(pcbnew.wxPointMM(dim * (3 + 1 / 2 + 1 / 4), dim * 3.5))
        holes[18].SetPosition(pcbnew.wxPointMM(dim * 14, dim * 1.5))
        holes[19].SetPosition(pcbnew.wxPointMM(dim * (11 - 1 / 4), dim * (2 + 1 / 2)))
        holes[20].SetPosition(pcbnew.wxPointMM(dim * (1 / 4 + 1 / 8), dim * 2.5))

        pcbnew.Refresh()


kb = Keyboard()
kb.place_footprints()
kb.remove_tracks()
# kb.add_tracks()
# kb.add_holes()
