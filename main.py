# -*- coding: utf-8 -*-
import copy
import numpy as np
import time

def read_data(file_crossword, file_dictionary):
    f_crossword = open(file_crossword, "r")
    f_dictionary = open(file_dictionary, "r")
    
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

def get_domini(variables, dictionary):
    """
    Assign each domini to its variable
    """
    for variable in variables:
        variable.append(dictionary[variable[2]])
    variables = np.array(variables)
    return variables

def get_every_position(variables):
    for variable in variables:
        if variable[1]: #vertical
            variable[0] = [(i+variable[0][0],variable[0][1]) for i in range(variable[2])]
        else: #horizontal
            variable[0] = [(variable[0][0],i+variable[0][1]) for i in range(variable[2])]
        
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
    
def get_good_domini(first_variable, queue_variables):
    """
    Return the variables that must get its domini changed.

    """
    good_ones = []
    queue_variables = np.array(queue_variables)
    for variable in queue_variables:
        intersection = [value for value in variable[0] if value in first_variable[0]]
        if len(intersection):
            good_ones.append(True)
        else:
            good_ones.append(False)
    return queue_variables[good_ones]

def update_domini(crossword, variables, word):
    """
    Applies forwardchecking
    """
    c_variables = np.copy(variables)
    variables_to_explore = get_good_domini(variables[0],c_variables[1:])
    #for each variable we will check its domini in the new crossword state
    for variable in c_variables[1:]:
        domini = np.array(variable[3])
        if any(np.array_equal(variable, i) for i in variables_to_explore):
            row = variable[0][0][0]
            col = variable[0][0][1]
            new_domini = []
            
            #get which positions have changed
            if variable[1]:  #vertical
                for i in range(row, variable[2]+row):
                    if crossword[i][col] != '0' and crossword[i][col] != '#':
                        new_domini.append((crossword[i][col], i-row))
            else: #horizontal
                for j in range(col, variable[2]+col):
                    if crossword[row][j] != '0' and crossword[row][j] != '#':
                        new_domini.append((crossword[row][j], j-col))
            
            #create a new domini with the words that fulfill the new restrictions
            for i in new_domini:
                domini = domini[np.char.find(domini, i[0], start = int(i[1])) == int(i[1])]
            
        #delete the last word inserted into the crossword from the variable's domini
        domini = np.delete(domini, np.where(domini == word))
        variable[3] = list(domini)
        if not domini.size: #if domini.size == 0 means that there will be an inevitable error
            return variables, False
    return c_variables, True


def getMinDomVars(var):
    """
    MRV, it returns every variable with the minimum domini
    """
    nou= []
    for i in var[:, 3]:
        nou.append(len(i))
    minVal = np.amin(nou)
    mrv_vars = var[nou==minVal]

    return mrv_vars

def perpendiculars(variables, vars):
    final = []
    for j in vars:
        perp = []
        for i in variables:
            if j[1] != i[1]:
                if j[0][0][j[1]] <= i[0][0][j[1]] <= j[0][0][j[1]] + j[2] - 1:
                    if i[0][0][i[1]] <= j[0][0][i[1]] <= i[0][0][i[1]] + i[2] - 1:
                        perp.append(i)
        final.append(len(perp))

    return final.index(max(final))

def solve_crossword(crossword, dictionary, variables):
    """
    Recursive algorithm that solves the crossword.
    """
    solution = None
    
    mrv_variables = getMinDomVars(variables)
    index_max = perpendiculars(variables, mrv_variables)
    index = np.where(np.all(variables == mrv_variables[index_max], axis=1))[0][0]
    variables[[0, index]] = variables[[index, 0]]

    variable = variables[0]
    domini = variable[3]
    for word in domini:
        c_crossword, valid = valid_word(crossword, word, variable[0][0][0],variable[0][0][1], variable[1])
        #print(c_crossword, '\n')
        if valid:
            c_variables, can_go = update_domini(c_crossword, variables, word) #it returns False if there is an empty domini
            if can_go:
                if not len(c_variables[1:]):
                    is_solved = True
                    solution = c_crossword
                else:
                    solution, is_solved = solve_crossword(c_crossword, dictionary, c_variables[1:])
                if is_solved:
                    return solution, is_solved
    return None, None

if __name__ == "__main__":
    m_dictionary, m_crossword = read_data("./data/crossword_CB_v2.txt","./data/diccionari_CB_v2.txt")
    m_variables = get_positions(m_crossword)
    get_length(m_crossword, m_variables)
    m_variables = get_domini(m_variables, m_dictionary)
    get_every_position(m_variables)
    
    time0 = time.time()
    solution = solve_crossword(m_crossword, m_dictionary, m_variables)
    time1 = time.time()
    print("Solution: \n", solution)
    print("In ", time1-time0, "seconds")
    

    m_dictionary, m_crossword = read_data("./data/crossword_A_v2.txt","./data/diccionari_A.txt")
    m_variables = get_positions(m_crossword)
    get_length(m_crossword, m_variables)
    m_variables = get_domini(m_variables, m_dictionary)
    get_every_position(m_variables)
    
    time0 = time.time()
    solution = solve_crossword(m_crossword, m_dictionary, m_variables)
    time1 = time.time()
    print("Solution: \n", solution)
    print("In ", time1-time0, "seconds")
 
    
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
