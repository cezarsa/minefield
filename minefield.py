# -*- coding: UTF-8 -*-

import random
import sys

class EndGameException(Exception):
    pass

class Minefield:
    BOMB = -1
    EMPTY = 0
    HIDDEN = "¦"
    SHOW = "S"
    MARK = "M"
    def __init__(self, sz_i, sz_j, qt_mines):
        if qt_mines > sz_i * sz_j:
            raise 'Quantidade de Minas Inválida' 
        self.sz_i = sz_i
        self.sz_j = sz_j
        self.qt_mines = qt_mines
        self.mark_count = 0
        self.mark_correct_count = 0
        self.show_count = 0
        self.main_matrix = [Minefield.EMPTY for i in range(sz_i * sz_j)]
        self.mask_matrix = [Minefield.HIDDEN for i in range(sz_i * sz_j)]

        rand_temp = [i for i in range(sz_i * sz_j)]
        for pos in range(qt_mines):
            rand_pos = random.randint(0, len(rand_temp) - 1)
            self.main_matrix[rand_temp[rand_pos]] = Minefield.BOMB
            rand_temp.remove(rand_temp[rand_pos])
            
        self.calculate_numbers()
        self.game_over = False

    def calculate_numbers(self):
        for pos, el in enumerate(self.main_matrix):
            if el == Minefield.BOMB:
                continue 
            i, j = self.to_pt(pos)
            self.main_matrix[pos] = self.qt_fields_around(i, j, Minefield.BOMB)

    def qt_fields_around(self, i, j, field):
        return sum([self.has_field(i + ii, j + jj, field) for ii in [-1,0,1] for jj in [-1,0,1]])
    
    def valid_point(self, i, j):
        return (i != None) and (j != None) and i >= 0 and j >= 0 and i < self.sz_i and j < self.sz_j

    def has_field(self, i, j, field):
        if field == Minefield.BOMB:
            return self.valid_point(i, j) and self.main_matrix[self.from_pt(i, j)] == field
        if field == Minefield.MARK:
            return self.valid_point(i, j) and self.mask_matrix[self.from_pt(i, j)] == field

    def to_pt(self, pos):
        return [pos / self.sz_j, pos % self.sz_j]

    def from_pt(self, i, j):
        return (i * self.sz_j) + j

    def debug_matrix(self):
        for pos, el in enumerate(self.main_matrix):
            if pos % self.sz_j == 0 and pos != 0:
                sys.stdout.write("\n")
            sys.stdout.write("%2s " % el)
        sys.stdout.write("\n")

    def masked_matrix(self):
        ret = [Minefield.EMPTY for i in range(self.sz_i * self.sz_j)]
        for pos, el in enumerate(self.main_matrix):
            if self.mask_matrix[pos] == Minefield.SHOW:
                ret[pos] = el
            else:
                ret[pos] = self.mask_matrix[pos]
        return ret
  
    def hit(self, i, j):
        if not self.valid_point(i, j):
            return
        pos = self.from_pt(i, j)
        if self.mask_matrix[pos] == Minefield.MARK:
            return 
        if self.main_matrix[pos] == Minefield.BOMB:
            self.mask_matrix[pos] = Minefield.SHOW
            self.game_over = True
            raise EndGameException("Fim jogo")
        elif self.main_matrix[pos] == Minefield.EMPTY:
            self.open_field(i, j)
        elif self.mask_matrix[pos] != Minefield.SHOW:
            self.mask_matrix[pos] = Minefield.SHOW
            self.show_count += 1

    def hit_around(self, i, j):
        if not self.valid_point(i, j):
            return
        pos = self.from_pt(i, j)
        if self.mask_matrix[pos] == Minefield.MARK or self.mask_matrix[pos] == Minefield.HIDDEN:
            return
        if self.main_matrix[pos] > self.qt_fields_around(i, j, Minefield.MARK):
            return
        [self.hit(i + ii, j + jj) for ii in [-1,0,1] for jj in [-1,0,1]]

    def mark(self, i, j):
        if not self.valid_point(i, j):
            return 
        pos = self.from_pt(i, j)
        if self.mask_matrix[pos] == Minefield.SHOW:
            return
        if self.mask_matrix[pos] == Minefield.HIDDEN:
            self.mask_matrix[pos] = Minefield.MARK
            self.mark_count += 1
            if self.has_field(i, j, Minefield.BOMB):
                self.mark_correct_count += 1
        elif self.mask_matrix[pos] == Minefield.MARK:
            self.mask_matrix[pos] = Minefield.HIDDEN
            self.mark_count -= 1
            if self.has_field(i, j, Minefield.BOMB):
                self.mark_correct_count -= 1

    def game_won(self):
        return self.mark_correct_count + self.show_count == self.sz_i * self.sz_j
        
    def open_field(self, i, j):
        if not self.valid_point(i, j):
            return
        pos = self.from_pt(i, j)
        if self.mask_matrix[pos] == Minefield.SHOW or self.mask_matrix[pos] == Minefield.MARK:
            return
        self.mask_matrix[pos] = Minefield.SHOW
        self.show_count += 1
        if self.main_matrix[pos] == Minefield.EMPTY:
            [self.open_field(i + ii, j + jj) for ii in [-1,0,1] for jj in [-1,0,1]]

#Minefield(16, 30, 20).debug_matrix()