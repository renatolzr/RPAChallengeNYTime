"""A friendly Python Utilitary."""

__version__ = "1.0"
__author__ = "Christiam Mendoza"

import os, sys, re, openpyxl, shutil
import csv

import logging
from logging import NullHandler
import subprocess
import configparser
import sqlite3
from sqlite3 import Error
from datetime import datetime ,timezone
from string import ascii_lowercase
import itertools
import fnmatch

LEVEL=logging.DEBUG

log=logging.getLogger(__name__)
log.addHandler(NullHandler())

def xlsx_to_csv(filename,sheet,newfilename,separator):
    
    xlsx = openpyxl.load_workbook(filename)
    sheet = xlsx.active
    data = sheet.rows

    csv = open(newfilename, "w+")

    for row in data:
        l = list(row)
        for i in range(len(l)):
            
            value=''
            
            if str(l[i].value) != "None":
                value=str(l[i].value)
            
            if i == len(l) - 1:
                csv.write(value)
            else:
                csv.write(value + separator)

        csv.write('\n')

    csv.close()
    

def create_folder_env(dir_path):
    '''
    Funcion que crea las carpetas de trabajo estándar de trabajo
    '''
    dir_in = os.path.join(dir_path,"input")
    dir_out = os.path.join(dir_path,"output")
    dir_log = os.path.join(dir_path,"log")
    
    if not os.path.exists(os.path.join(dir_in,"backup")):
        os.makedirs( os.path.join(dir_in,"backup") )
    
    if not os.path.exists(os.path.join(dir_out,"backup")):
        os.makedirs( os.path.join(dir_out,"backup") )

    if not os.path.exists(dir_log):
        os.makedirs( dir_log )    
    
def config_logging(file_log="", level=LEVEL, console=True):
    '''
    Funcion que configura la gestion de Logs
    '''
    #logging file
    if file_log != "":
        logging.basicConfig( format = '%(asctime)-5s %(filename)s %(lineno)d %(levelname)-8s %(message)s', level = logging.DEBUG, filename = file_log, filemode = "a" )
    
    log=logging.getLogger(__name__)
    
    # logging console
    if console:
        console = logging.StreamHandler()
        console.setLevel(level)
        log.addHandler(console)

    return log

def check_if_string_in_file(filename, string_to_search):
    """ Check if any line in the file contains given string """
    # Open the file in read only mode
    with open(filename, 'r') as read_obj:
        # Read all lines in the file one by one
        for line in read_obj:
            # For each line, check if line contains the string
            if string_to_search.lower() in line.lower():
                return True
    return False



class Configuration(object):
    """
    Clase que permite cargar dinámicamente los archivos de configuración del proceso.    """
    
    def __init__(self, file_config="Config.ini", section_names=["DEFAULT"]):
        r"""Inicializa los parametros de entrada
        :param file_config: Ruta absoluta del archivo de configuración.
        :param section_names: (optional) Lista de secciones a cargar.
        :return: :class: object
        """
        parser = configparser.ConfigParser()
        parser.optionxform = str  
        found = parser.read(file_config)

        if not found:
            raise ValueError('Archivo de configuracion no encontrado.')
        
        self.parser = parser

        # Cargando configuracion
        for name in section_names:
            self.__dict__.update(parser.items(name))


def get_now_format(format = "%Y%m%d%H%M%S%f"):
    return str(datetime.now().strftime(format))

def replace_string_in_file(filename_in, filename_out, dict_words):
    """ Reemplaza cadenas de un archivo
    :param filename_in: Archivo de entrada
    :param filename_out: Archivo de salida
    :param dict_words: Diccionario de palabras y valores a reemplazar
    :return: None
    """

    write_obj = open(filename_out, 'w')

    line = ""

    with open(filename_in, 'r') as read_obj:
        for line in read_obj:

            for k, v in dict_words.items():
                line = line.replace(k, v)

            #log.debug(line)
            write_obj.write(line)

    write_obj.close()



def iter_all_strings():
    """ Generator que devuelve lista de letras secuenciales
    :return: yield
    """
    for size in itertools.count(1):
        for s in itertools.product(ascii_lowercase, repeat=size):
            yield "".join(s)