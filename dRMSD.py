#!/usr/bin/env python2.7

""" Calculates dRMSD for atomic structures (assumes atom names are the same).
(C) Aleksandra Jarmolinska 2019 a.jarmolinska@mimuw.edu.pl"""

import sys
import re
from collections import namedtuple
import math

Atom = namedtuple("Atom","name x y z")

def readPdb(handle):
    atom = re.compile("ATOM  .{7}([ A-Z0-9']{3}).{6}[0-9 ]{4}.{4}([0-9\. -]{8})([0-9\. -]{8})([0-9\. -]{8})")
    #atom = re.compile("ATOM  .{7}([ A-Z0-9']{3}).{6}[0-9 ]{4}.{4}([0-9\. -]{8})([0-9\. -]{8})([0-9\. -]{8}).{23}[A-Z]")
    with open(handle) as input_file:
        s = {}
        for line in input_file:
            if atom.match(line):
                a = map(lambda x: x.strip(),atom.findall(line)[0])
                s[a[0]] = Atom(a[0],*map(float,a[1:]))
    return s

def readModelsPdb(handle):
    models = []
    atom = re.compile("ATOM  .{7}([ A-Z0-9']{3}).{6}[0-9 ]{4}.{4}([0-9\. -]{8})([0-9\. -]{8})([0-9\. -]{8})")
    with open(handle) as input_file:
        s = {}
        for line in input_file:
            if atom.match(line):
                a = map(lambda x: x.strip(),atom.findall(line)[0])
                s[a[0]] = Atom(a[0],*map(float,a[1:]))
            elif re.match("^ENDMDL", line):
                models.append(s)
                s = {}
    return models

def distance(a,b):
    return math.sqrt(math.pow(a.x-b.x,2)+math.pow(a.y-b.y,2)+math.pow(a.z-b.z,2))

def dRMSD(s1,s2):
    """Calculates dRMSD between two structures on all atom pairs"""
    all_atoms = sorted(s1.keys())
    suma = 0
    cnt=0
    for i,a in enumerate(all_atoms):
        for b in all_atoms[i+1:]:
            dist_1 = distance(s1[a], s1[b])
            dist_2 = distance(s2[a], s2[b])
            suma += math.pow(dist_1-dist_2,2)
            cnt += 1
    return math.sqrt(suma/cnt)

def models_dRMSD(models,sdev=1):
    """Calculates dRMSD of all models vs all models,
    disregarding atom pairs with standard deviation below ::sdev::"""
    all_atoms = sorted(models[0].keys())
    atom_drmsds = []
    mcnt = 0
    model_drmsds = {}
    for i,a in enumerate(all_atoms):
        for b in all_atoms[i+1:]:
            atom_drmsds.append([])
            for _1,m1 in enumerate(models):
                for _2,m2 in enumerate(models[_1+1:]):
                    dist_1 = distance(m1[a], m1[b])
                    dist_2 = distance(m2[a], m2[b])
                    mcnt += 1
                    atom_drmsds[-1].append(dist_1-dist_2)
            avg = sum(atom_drmsds[-1])/len(atom_drmsds[-1])
            keep = math.sqrt(sum([math.pow(v-avg,2) for v in atom_drmsds[-1]])/len(atom_drmsds[-1])) #< sdev
            #print a,b,avg, keep#,#len(atom_drmsds[-1]), atom_drmsds[-1]
            if keep < sdev:
                atom_drmsds.pop() #removes last column, as it doesn't add anything
            else:
                _=0
                for _1, m1 in enumerate(models):
                    for _2, m2 in enumerate(models[_1 + 1:]):
                        model_drmsds[(_1,_2+_1+1)] = model_drmsds.get((_1,_2+_1+1),0) + math.pow(atom_drmsds[-1][_],2)
                        _ += 1
    for _1, m1 in enumerate(models):
        for _2,m2 in enumerate(models[_1 + 1:]):
            print "Model {} - model {} : {}".format(_1,_2+_1+1,math.sqrt(model_drmsds[(_1,_2+_1+1)]/len(atom_drmsds)))
    return


if __name__ == "__main__":
    if len(sys.argv) == 2:
        models = readModelsPdb(sys.argv[1])
        models_dRMSD(models)
    else:
        s1 = readPdb(sys.argv[1])
        s2 = readPdb(sys.argv[2])
        print dRMSD(s1, s2)

