# -*- coding: UTF-8 -*-
from minefield import *
from wx.lib.wordwrap import wordwrap
import wx
import pickle
import os
import time


class GameConfig:
    NIVEIS = [[9, 9, 10], [16, 16, 40], [16, 30, 99], [30, 40, 250]]
    def __init__(self):
        self.set_nivel(2)
        self.bg_img = "img2.jpg"
        self.bg_pos = [120, 220]
        self.flag_img = "flag.png"
        self.bomb_img = "bomb.png"
        self.restart_game()
        
    def restart_game(self):
        self.minefield = Minefield(self.minefield_sz[0], self.minefield_sz[1], self.qt_mines)
        
    def set_nivel(self, nivel):
        self.minefield_sz = [GameConfig.NIVEIS[nivel][0], GameConfig.NIVEIS[nivel][1]]
        self.qt_mines = GameConfig.NIVEIS[nivel][2]

class MinefieldFrame(wx.Frame):
    ID_NOVO_JOGO = 10
    ID_JOGO_FACIL = 11
    ID_JOGO_INTER = 12
    ID_JOGO_DIFICIL = 13
    ID_JOGO_ULTRA = 14
    ID_ABRIR_JOGO = 15
    ID_SALVAR_JOGO = 16
    WILDCARD = "Campo Minado Salvo (*.minefield)|*.minefield"
    
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title, pos = [15, 15],
                          style = wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        menuBar = wx.MenuBar()
        menu = wx.Menu()
        menu.Append(self.ID_NOVO_JOGO, "&Novo\tF2", "Novo jogo")
        menu.Append(self.ID_ABRIR_JOGO, "&Abrir...", "Abrir jogo")
        menu.Append(self.ID_SALVAR_JOGO, "&Salvar...", "Salvar jogo")
        menu.Append(wx.ID_SEPARATOR, kind = wx.ITEM_SEPARATOR)
        menu.Append(self.ID_JOGO_FACIL, "&Fácil", "Nível fácil")
        menu.Append(self.ID_JOGO_INTER, "&Intermediário", "Nível intermediário")
        menu.Append(self.ID_JOGO_DIFICIL, "&Difícil", "Nível difícil")
        menu.Append(self.ID_JOGO_ULTRA, "&Ultra", "Nível ultra-mega-impossível")
        menu.Append(wx.ID_SEPARATOR, kind = wx.ITEM_SEPARATOR)
        menu.Append(wx.ID_EXIT, "Sai&r\tAlt-X", "Sair")

        menuHelp = wx.Menu()
        menuHelp.Append(wx.ID_ABOUT, "&Sobre...\tF1", "Sobre o jogo")

        menuBar.Append(menu, "&Jogo")
        menuBar.Append(menuHelp, "&Ajuda")        

        self.SetMenuBar(menuBar)
        self.CreateStatusBar()

        self.gameConfig = GameConfig()
        self.headerWin = HeaderWindow(self)
        header_height = self.headerWin.calculateHeaderHeight()
        self.gameWin = GameWindow(self, wx.Point(0, header_height), self.headerWin)
        self.ConfigGame()

        self.Bind(wx.EVT_MENU, self.OnNovoJogo, id = self.ID_NOVO_JOGO)
        self.Bind(wx.EVT_MENU, self.OnAbrirJogo, id = self.ID_ABRIR_JOGO)
        self.Bind(wx.EVT_MENU, self.OnSalvarJogo, id = self.ID_SALVAR_JOGO)
        self.Bind(wx.EVT_MENU_RANGE, self.OnNivelJogo, id = self.ID_JOGO_FACIL, id2 = self.ID_JOGO_ULTRA)
        self.Bind(wx.EVT_MENU, self.OnClose, id = wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnAbout, id = wx.ID_ABOUT)

    def ConfigGame(self):
        self.gameWin.config_minefield(self.gameConfig)
        self.headerWin.config(self.gameConfig)
        header_height = self.headerWin.calculateHeaderHeight()
        size = self.gameWin.calculateGameSize()
        
        self.headerWin.SetSize(wx.Size(size.width, header_height))
        self.gameWin.SetSize(wx.Size(size.width, size.height))
        
        size.height += header_height
        self.SetClientSize(size)

    def OnNivelJogo(self, evt):
        self.gameConfig.set_nivel(evt.GetId() - self.ID_JOGO_FACIL)
        self.gameConfig.restart_game()
        self.ConfigGame()
        
    def OnNovoJogo(self, evt):
        self.gameConfig.restart_game()
        self.ConfigGame()

    def OnAbrirJogo(self, evt):
        self.gameWin.block()
        dlg = wx.FileDialog(
            self, message="Escolha um jogo salvo", defaultDir = os.getcwd(), 
            defaultFile = "", wildcard = self.WILDCARD, style = wx.FD_OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            fp = file(path, "rb")
            self.gameConfig = pickle.load(fp)
            fp.close()
            self.ConfigGame()
        dlg.Destroy()
        self.gameWin.unblock()
        
    def OnSalvarJogo(self, evt):
        self.gameWin.block()
        dlg = wx.FileDialog(
            self, message="Salvar jogo como...", defaultDir = os.getcwd(), 
            defaultFile = "", wildcard = self.WILDCARD, style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            fp = file(path, 'wb')
            pickle.dump(self.gameConfig, fp)
            fp.close()
        dlg.Destroy()
        self.gameWin.unblock()
        
    def OnAbout(self, evt):
        info = wx.AboutDialogInfo()
        info.Name = "Campo Minado de Kênia"
        info.Version = "0.1 Beta"
        info.Copyright = "(C) 2008 Cezar Sá Espinola"
        info.Description = wordwrap(
            "Feito especialmente para Kênia da Silva Farias Espinola, esposa de Cezar. "
            "A mulher mais linda e mais amada do mundo todo!",
            350, wx.ClientDC(self))
        info.WebSite = ("javascript: document.write('<h1>Eu Te AMO!</h1>');", "Eu te Amo!!!")
        wx.AboutBox(info)
        
    def OnClose(self, evt):
        self.Close()

class Rect:
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

class HeaderWindow(wx.Window):
    TIMER_ID = 999
    def __init__(self, parent):
        wx.Window.__init__(self, parent, pos = wx.Point(0, 0), style = wx.NO_BORDER)
        self.area_height = 50
        self.time_sz = [60, 25]
        self.mark_sz = [60, 25]
        self.margin = Rect(10, 6, 10, 6)
        self.time_bg_color = wx.Colour(128, 134, 151)
        self.mark_bg_color = wx.Colour(128, 134, 151)
        self.shadow_color = wx.Colour(0, 0, 0)
        self.bg_color = wx.Colour(120, 120, 120)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_resize)
        self.Bind(wx.EVT_TIMER, self.on_timer)
        self.timer = wx.Timer(self, HeaderWindow.TIMER_ID)
        self.start_time = -1

    def start_timer(self):
        self.current_time = 0
        self.start_time = time.time()
        self.timer.Start(200)

    def stop_timer(self):
        self.start_time = -1
        self.timer.Stop()

    def on_timer(self, event):
        self.current_time = int(time.time() - self.start_time)
        self.Refresh(False)
        self.Update()

    def on_resize(self, event):
        self.Refresh(False)
        self.Update()

    def config(self, gameConfig):
        self.stop_timer()
        self.current_time = 0
        self.gameConfig = gameConfig
        self.Refresh(False)
        self.Update()
        
    def calculateHeaderHeight(self):
        return max(self.time_sz[1], self.mark_sz[1]) + self.margin.top + self.margin.bottom

    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self)
        sz = self.GetSize()

        font = dc.GetFont()
        font.SetPointSize(10)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        dc.SetFont(font)
        
        dc.SetBrush(wx.Brush(self.bg_color, wx.SOLID))
        dc.SetPen(wx.Pen(self.bg_color, 0))
        dc.DrawRectangle(0, 0, sz[0], sz[1])

        x, y = self.margin.left, self.margin.top
        dc.SetBrush(wx.Brush(self.shadow_color, wx.SOLID))
        dc.SetPen(wx.Pen(self.shadow_color, 0))
        dc.DrawRectangle(x + 2, y + 2, self.mark_sz[0], self.mark_sz[1])

        dc.SetBrush(wx.Brush(self.mark_bg_color, wx.SOLID))
        dc.SetPen(wx.Pen(self.mark_bg_color, 0))
        dc.DrawRectangle(x, y, self.mark_sz[0], self.mark_sz[1])

        mark_str = str(self.gameConfig.minefield.mark_count) + '/' + str(self.gameConfig.minefield.qt_mines)
        str_sz = dc.GetTextExtent(mark_str)
        dc.DrawText(mark_str, x + (self.mark_sz[0] / 2) - (str_sz[0] / 2),
                              y + (self.mark_sz[1] / 2) - (str_sz[1] / 2))

        x, y = sz[0] - self.margin.right - self.time_sz[0], self.margin.top
        dc.SetBrush(wx.Brush(self.shadow_color, wx.SOLID))
        dc.SetPen(wx.Pen(self.shadow_color, 0))
        dc.DrawRectangle(x + 2, y + 2, self.time_sz[0], self.time_sz[1])
        
        dc.SetBrush(wx.Brush(self.time_bg_color, wx.SOLID))
        dc.SetPen(wx.Pen(self.time_bg_color, 0))
        dc.DrawRectangle(x, y, self.time_sz[0], self.time_sz[1])

        time_str = str(self.current_time)
        str_sz = dc.GetTextExtent(time_str)
        dc.DrawText(time_str, x + (self.time_sz[0] / 2) - (str_sz[0] / 2),
                              y + (self.time_sz[1] / 2) - (str_sz[1] / 2))
        


class GameWindow(wx.Window):
    def __init__(self, parent, win_pos, header_win):
        wx.Window.__init__(self, parent, pos = win_pos, style = wx.NO_BORDER)

        self.header_win = header_win
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse_events)

        self.margin = Rect(0, 0, 0, 0)
        self.block_size = wx.Size(18, 18)
        self.block_frame = wx.Size(1, 1)

        self.margin_color = wx.BLACK
        self.block_color = {
            Minefield.HIDDEN: wx.Colour(100, 100, 100),
            Minefield.MARK: wx.Colour(128, 0, 255),
            Minefield.BOMB: wx.Colour(200, 0, 0),
            Minefield.EMPTY: wx.Colour(200, 200, 200)
        }
        self.block_frame_color = wx.Colour(220, 220, 220)
        self.block_number_bg_color = wx.Colour(200, 200, 200)
        self.block_number_colors = [
            wx.Colour(0, 0, 255), 
            wx.Colour(0, 128, 0), 
            wx.Colour(255, 0, 0), 
            wx.Colour(0, 0, 128), 
            wx.Colour(128, 0, 0), 
            wx.Colour(0, 128, 128), 
            wx.Colour(0, 0, 0), 
            wx.Colour(128, 128, 128)
        ]
        self.highlight_bitmap = self.make_bitmap(self.block_size.width, self.block_size.height, 255, 255, 0, 150)

    def config_minefield(self, gameConfig):
        self.minefield = gameConfig.minefield
        self.bg_bitmap = wx.Bitmap(gameConfig.bg_img)
        self.bg_bitmap = self.bg_bitmap.GetSubBitmap(
            wx.Rect(gameConfig.bg_pos[0], gameConfig.bg_pos[1],
                    self.bg_bitmap.GetWidth() - gameConfig.bg_pos[0],
                    self.bg_bitmap.GetHeight() - gameConfig.bg_pos[1]))
        self.flag_bitmap = wx.Bitmap(gameConfig.flag_img)
        self.bomb_bitmap = wx.Bitmap(gameConfig.bomb_img)
        self.ignoreLeftUp = self.ignoreRightUp = False
        self.is_blocked = False
        self.is_unblock = False
        self.has_blocked_event = 0
        self.old_pos = False
        self.highlight_around = False
        self.is_first_move = True
        self.Refresh(False)
        self.Update()
        
    def make_bitmap(self, width, height, red, green, blue, alpha):
        bmp = wx.EmptyBitmap(width, height + 1, 32)
        pixelData = wx.AlphaPixelData(bmp)
        for pixel in pixelData:
            pixel.Set(red, green, blue, alpha)
        return bmp
        
    def calculateGameSize(self):
        width = (self.block_size.width * self.minefield.sz_j) + \
                (self.block_frame.width * (self.minefield.sz_j - 1)) + \
                self.margin.left + self.margin.right
        height = (self.block_size.height * self.minefield.sz_i) + \
                (self.block_frame.height * (self.minefield.sz_i - 1)) + \
                self.margin.top + self.margin.bottom
        return wx.Size(width, height)

    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self)
        dc.Clear()
        font = dc.GetFont()
        font.SetPointSize(10)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        dc.SetFont(font)
        sz = self.GetSize()

        if self.bg_bitmap:
            init_pos = [self.margin.left, self.margin.top]
            while init_pos[0] < sz.width:
                dc.DrawBitmap(self.bg_bitmap, init_pos[0], init_pos[1], False)
                init_pos[1] = self.margin.top
                while init_pos[1] < sz.height:
                    dc.DrawBitmap(self.bg_bitmap, init_pos[0], init_pos[1], False)
                    init_pos[1] += self.bg_bitmap.GetHeight()
                init_pos[0] += self.bg_bitmap.GetWidth()
 
        dc.SetBrush(wx.Brush(self.margin_color, wx.SOLID))
        dc.SetPen(wx.Pen(self.margin_color, 0))
        dc.DrawRectangle(0, 0, sz.width, self.margin.top)
        dc.DrawRectangle(0, 0, self.margin.left, sz.height)
        dc.DrawRectangle(0, sz.height - self.margin.bottom, sz.width, self.margin.bottom)
        dc.DrawRectangle(sz.width - self.margin.right, 0, self.margin.right, sz.height)

        dc.SetBrush(wx.Brush(self.block_frame_color, wx.SOLID))
        dc.SetPen(wx.Pen(self.block_frame_color, 0))
        for j in range(self.minefield.sz_j - 1):
            cpos_x = self.block_size.width + (j * (self.block_size.width + self.block_frame.width))
            dc.DrawRectangle(cpos_x, 0, self.block_frame.width, sz.height)

        for i in range(self.minefield.sz_i - 1):
            cpos_y = self.block_size.height + (i * (self.block_size.height + self.block_frame.height))
            dc.DrawRectangle(0, cpos_y, sz.width, self.block_frame.height)

        matrix = self.minefield.masked_matrix()
        for pos, el in enumerate(matrix):
            i, j = self.minefield.to_pt(pos)
            is_highlight_block = False
            is_number = False
            if (el == Minefield.HIDDEN) and \
                    (self.highlight_around != False and ( \
                    (i == self.highlight_around[0] - 1 and j == self.highlight_around[1] - 1) or \
                    (i == self.highlight_around[0] - 1 and j == self.highlight_around[1]) or \
                    (i == self.highlight_around[0] - 1 and j == self.highlight_around[1] + 1) or \
                    (i == self.highlight_around[0] and j == self.highlight_around[1] - 1) or \
                    (i == self.highlight_around[0] and j == self.highlight_around[1]) or \
                    (i == self.highlight_around[0] and j == self.highlight_around[1] + 1) or \
                    (i == self.highlight_around[0] + 1 and j == self.highlight_around[1] - 1) or \
                    (i == self.highlight_around[0] + 1 and j == self.highlight_around[1]) or \
                    (i == self.highlight_around[0] + 1 and j == self.highlight_around[1] + 1))):
                is_highlight_block = True
            elif (el == Minefield.HIDDEN or el == Minefield.MARK) and self.old_pos and i == self.old_pos[0] and j == self.old_pos[1]:
                is_highlight_block = True
            elif el in self.block_color.keys():
                dc.SetBrush(wx.Brush(self.block_color[el], wx.SOLID))
                dc.SetPen(wx.Pen(self.block_color[el], 0))
            else:
                dc.SetBrush(wx.Brush(self.block_number_bg_color, wx.SOLID))
                dc.SetPen(wx.Pen(self.block_number_bg_color, 0))
                dc.SetTextForeground(self.block_number_colors[el - 1])
                is_number = True

            x, y = self.margin.left + (j * (self.block_size.width + self.block_frame.width)), \
                   self.margin.top + (i * (self.block_size.height + self.block_frame.height))
            if el != Minefield.HIDDEN or (not self.bg_bitmap):
                dc.DrawRectangle(x, y, self.block_size.width, self.block_size.height)

            if el == Minefield.MARK and self.flag_bitmap:
                dc.DrawBitmap(self.flag_bitmap,
                              x + (self.block_size.width / 2) - (self.flag_bitmap.GetWidth() / 2),
                              y + (self.block_size.height / 2) - (self.flag_bitmap.GetHeight() / 2),
                              True)
            
            if el == Minefield.BOMB and self.bomb_bitmap:
                dc.DrawBitmap(self.bomb_bitmap,
                              x + (self.block_size.width / 2) - (self.bomb_bitmap.GetWidth() / 2),
                              y + (self.block_size.height / 2) - (self.bomb_bitmap.GetHeight() / 2),
                              True)
            
            if is_number:
                str_sz = dc.GetTextExtent(str(el))
                dc.DrawText(str(el), x + (self.block_size.width / 2) - (str_sz[0] / 2),
                            y + (self.block_size.height / 2) - (str_sz[1] / 2))

            if is_highlight_block:
                dc.DrawBitmap(self.highlight_bitmap, x, y, True)

    def position_to_matrix_pos(self, point):
        win_sz = self.GetSize()
        point.x -= self.margin.left
        point.y -= self.margin.top
        if  point.x < 0 or point.y < 0 or \
              point.x > win_sz.width - self.margin.right - self.margin.left or \
              point.y > win_sz.width - self.margin.top - self.margin.bottom or \
              point.x % (self.block_size.width + self.block_frame.width) > self.block_size.width or \
              point.y % (self.block_size.height + self.block_frame.height) > self.block_size.height:
            return False
        pos_i = point.y / (self.block_size.height + self.block_frame.height)
        pos_j = point.x / (self.block_size.width + self.block_frame.width)
        return [pos_i, pos_j]

    def block(self):
        self.is_blocked = True
        self.has_blocked_event = 0
        
    def unblock(self):
        if self.is_blocked:
            self.is_unblock = True
        
    def on_mouse_events(self, event):
        event.Skip()
        if self.ignoreLeftUp and event.LeftUp():
            self.ignoreLeftUp = False
            return
        elif self.ignoreRightUp and event.RightUp():
            self.ignoreRightUp = False
            return
        if self.is_unblock and self.has_blocked_event == -1 or self.has_blocked_event > 5:
            self.is_blocked = False
            self.is_unblock = False
        if self.is_blocked:
            if event.ButtonDown() or event.ButtonUp():
                self.has_blocked_event = -1
            else:
                self.has_blocked_event += 1
            return
        
        matrix_pos = self.position_to_matrix_pos(event.GetPosition())
        repaint = False
        if matrix_pos != False:
            if event.LeftIsDown() and event.RightUp() or event.RightIsDown() and event.LeftUp():
                if event.LeftIsDown(): self.ignoreLeftUp = True
                elif event.RightIsDown(): self.ignoreRightUp = True
                try:
                    self.minefield.hit_around(*matrix_pos)
                except EndGameException:
                    pass
                repaint = True
            elif event.LeftUp():
                try:
                    self.minefield.hit(*matrix_pos)
                    if self.is_first_move:
                       self.is_first_move = False
                       self.header_win.start_timer()
                except EndGameException:
                    pass
                repaint = True
            elif event.RightUp():
                self.minefield.mark(*matrix_pos)
                repaint = True
            if event.LeftIsDown() and event.RightIsDown():
                self.highlight_around = matrix_pos
                repaint = True
            else:
                self.highlight_around = False
            if self.old_pos == False or self.old_pos[0] != matrix_pos[0] or self.old_pos[1] != matrix_pos[1]:
                repaint = True
            self.old_pos = matrix_pos
        else:
            self.old_pos = False
        if self.minefield.game_won():
            self.animate_winning()
            self.block()
            self.highlight_around = False
            self.old_pos = False
            self.header_win.stop_timer()
            repaint = True
        elif self.minefield.game_over:
            self.animate_lose()
            self.block()
            self.highlight_around = False
            self.old_pos = False
            self.header_win.stop_timer()
            repaint = True
        if repaint:
            self.header_win.Refresh(False)
            self.header_win.Update()
            self.Refresh(False)
            self.Update()

    def animate_winning(self):
        pass

    def animate_lose(self):
        pass

class MyApp(wx.App):
    def OnInit(self):
        frame = MinefieldFrame(None, "Campo Minado de Kênia")
        self.SetTopWindow(frame)
        frame.Show(True)
        return True
        
app = MyApp(redirect=False)
app.MainLoop()