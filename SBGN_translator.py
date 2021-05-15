# -*- coding: utf-8 -*-
"""
Created on Tue May  4 10:50:49 2021

@author: 52935
"""
################extract information from SBML ###################33
import  xml.dom.minidom
import optparse

usage="usage: trranslator of PD SBGN maps"
parser = optparse.OptionParser(usage=usage,version="%prog 1.1")
parser.add_option("-i","--input",dest="inputfile",help='input SBGN maps',metavar="FILE")
parser.add_option("-o","--output",dest="outputfile",help='output translation result',metavar="FILE")
options = parser.parse_args()
inputf=options.inputfile
outputf=options.outputfile


dom = xml.dom.minidom.parse(inputf)

root = dom.documentElement
glyph=root.getElementsByTagName('glyph')
arc=root.getElementsByTagName('arc')
Entity_list=['macromolecule','simple chemical','tag','complex','nucleic acid feature','macromolecule multimer',
             'perturbing agent','source and sink','unspecified entity','phenotype']
Process_list=['process','uncertain process','omitted process', 'association','dissociation']
logic_arc_list=['logic arc', 'equivalence arc']
Entity={}
Process={}
Arc={}
dic = {'consumption':"",
       'catalysis':"catalysed by ",
       'production':"produce ",
       'necessary stimulation' : "stimulated by ",
       'inhibition': 'inhibit ',
       'modulation':'modulate ',
       'equivalence arc':'equivalate ',
       'stimulation':'stimulated by'}


for i in glyph:
    classes=i.getAttribute('class')
    if classes in Process_list:
        Process[i.getAttribute('id')]=[]
        port= i.getElementsByTagName('port')
        for po in port:
            Process[i.getAttribute('id')].append(po.getAttribute('id'))
    if classes in Entity_list:
        chemical_name = i.getElementsByTagName('label')[0].getAttribute('text').replace('\n','')
        chemical_state = ""
        if len(i.getElementsByTagName('glyph')) > 0:
            for j in i.getElementsByTagName('glyph'):
                if len(j.getElementsByTagName('state')) > 0:
                    chemical_state = chemical_state + "_" + j.getElementsByTagName('state')[0].getAttribute('value')
                if len(j.getElementsByTagName('label')) > 0:   
                    chemical_state = chemical_state + "_" + j.getElementsByTagName('label')[0].getAttribute('text')
        Entity[i.getAttribute('id')]=chemical_name + chemical_state

for k in arc:
    Arc[k.getAttribute('id')]={'class':k.getAttribute('class'),
                               'source':k.getAttribute('source'),
                               'target':k.getAttribute('target'),
                               'use':0}
################ compartment of sentence ####################
with open(outputf,'w') as f:
    for ids in Process:
        Front={}
        Back={}
        sentence='process:'
        pro_set=Process[ids]
        pro_set.append(ids)
        for key in Arc:
            if Arc[key]['source'] in pro_set:
                if Arc[key]['class'] not in Back:
                    Back[Arc[key]['class']]=[Arc[key]['target']]
                else:
                    Back[Arc[key]['class']].append(Arc[key]['target'])
                Arc[key]['use']=1
            if Arc[key]['target'] in pro_set:
                if Arc[key]['class'] not in Front:
                    Front[Arc[key]['class']]=[Arc[key]['source']]
                else:
                    Front[Arc[key]['class']].append(Arc[key]['source'])
                Arc[key]['use']=1
        
################## construct the human-readible sentence #############
        for types in Front:
            sentence = sentence+' '+dic[types]
            for info in Front[types]:
                sentence = sentence + Entity[info] +','
            sentence = sentence+'/'
    
        for types in Back:
            sentence = sentence+' '+dic[types]
            for info in Back[types]:
                sentence = sentence + Entity[info] +','
            sentence = sentence+'/'
        
        f.write(sentence+'.')
   
        for key in Arc:
            sentence=''
            if Arc[key]['use'] == 0:
                sentence = sentence+Entity[Arc[key]['target'].split('.')[0]] + ' ' + dic[Arc[key]['class']] + ' ' + Entity[Arc[key]['source'].split('.')[0]] + '.'
                f.write(sentence)
            
