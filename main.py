# -*- coding: utf-8 -*-

import numpy as np
import time

def read_data():
    #f_crossword = open("./data/crossword_A_v2.txt", "r")
    #f_dictionary = open("./data/diccionari_A.txt", "r")
    f_crossword = open("./data/crossword_CB_v2.txt", "r")
    f_dictionary = open("./data/diccionari_CB_v2.txt", "r")
    
    aux_crossword = [line.split() for line in f_crossword]
    m_crossword = np.array(aux_crossword)
    
    m_dictionary = {}
    for word in f_dictionary:
        word = word.rstrip('\n')
        if len(word) not in m_dictionary:
            m_dictionary[len(word)] = [word]
        else:
            m_dictionary[len(word)].append(word)
        
    f_crossword.close()
    f_dictionary.close()
    
    return m_dictionary, m_crossword

def get_positions(crossword):
    """
    Get valid positions where each word begins and its orientation.
    """
    variables = [] # (row, col), direction False=horizontal True=vertical
    for i in range(len(crossword)):
        for j in range(len(crossword[i])):
            if (i-1 < 0 or j-1 < 0) and crossword[i][j] == '0': #border words
                if i-1 < 0 and crossword[i+1][j] == '0':
                    variables.append([(i,j),True]) #vertical
                if j-1 < 0 and crossword[i][j+1] == '0':
                    variables.append([(i,j),False]) #horizontal
                if i-1 < 0 and j+1 < len(crossword[i]) and crossword[i][j+1] == '0' and crossword[i][j-1] == '#': 
                    variables.append([(i,j),False]) #horizontal
                if j-1 < 0 and i+1 < len(crossword) and crossword[i+1][j] == '0' and crossword[i-1][j] == '#': 
                    variables.append([(i,j),True]) #vertical
            elif crossword[i][j] == '0': #inner words
                if crossword[i][j-1] == '#' and j+1 < len(crossword[i]) and crossword[i][j+1] == '0':
                    variables.append([(i,j),False]) #horizontal
                if crossword[i-1][j] == '#' and i+1 < len(crossword) and crossword[i+1][j] == '0':
                    variables.append([(i,j),True]) #vertical
    
    return variables

def get_length(crossword, variables):
    """
    Get the length of each word to be written.
    """
    for variable in variables:
        length = 0
        direction = variable[1]
        row = variable[0][0]
        col = variable[0][1]
        if direction: #vertical
            for i in range(row, len(crossword)):
                if crossword[i][col] == '0':
                    length += 1
                else:
                    break
        else: #horizontal
            for j in range(col, len(crossword[row])):
                if crossword[row][j] == '0':
                    length += 1
                else:
                    break
        variable.append(length)

def valid_word(crossword, word, row, col, direction):
    """
    Check if a certain word is valid in a certain row or column and it writes the word in the crossword
    """
    valid = True
    c_crossword = np.copy(crossword)
    if direction: #vertical
        for i in range(row, len(word)+row):
            if crossword[i][col] == '0' or crossword[i][col] == word[i-row]:
                c_crossword[i][col] = word[i-row]
            else:
               valid = False
               break
    else: #horizontal
        for j in range(col, len(word)+col):
            if crossword[row][j] == '0' or crossword[row][j] == word[j-col]:
                c_crossword[row][j] = word[j-col]
            else:
                valid = False
                break

    if valid:
        return c_crossword, valid
    else:
        return crossword, valid
    
def solve_crossword(crossword, dictionary, variables, n):
    """
    Recursive algorithm that solves the crossword.
    """
    solution = None
    variable = variables[n]
    list_words = dictionary[variable[2]]
    for word in list_words:
        c_crossword, valid = valid_word(crossword, word, variable[0][0],variable[0][1], variable[1])
        print(c_crossword, '\n')
        if valid:
            if n == (len(variables)-1):
                is_solved = True
                solution = c_crossword
            else:
                solution, is_solved = solve_crossword(c_crossword, dictionary, variables, n+1)
            if is_solved:
                return solution, is_solved
                    
    return None, None

if __name__ == "__main__":
    m_dictionary, m_crossword = read_data()
    m_variables = get_positions(m_crossword)
    get_length(m_crossword, m_variables)
    
    time0 = time.time()
    solution = solve_crossword(m_crossword, m_dictionary, m_variables, 0)
    time1 = time.time()
    print("Solution: \n", solution)
    print("In ", time1-time0, "seconds")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
