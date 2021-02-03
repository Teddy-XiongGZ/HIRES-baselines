import re
import math
import spacy
import argparse
from itertools import islice
from multiprocessing import Process


parser = argparse.ArgumentParser()
parser.add_argument('input_file', action='store', type=str,
                    help='The path to input file')
parser.add_argument('text_length', action='store', type=str,
                    help='The num of rows of the input file')
parser.add_argument('output_file', action='store', type=str,
                    help='The path to output file')
parser.add_argument('error_file', action='store', type=str,
                    help='The path to output error')
parser.add_argument('-m', '--multiprocess', action='store_true', default=False,
                    help='used for multiprocess')


args = parser.parse_args()
input_file = args.input_file
text_length = args.text_length
error_file = args.error_file
output_file = args.output_file
multiprocess = args.multiprocess


splitter = spacy.load('en_core_web_sm')


def strip_title(sub_str):
    r = re.search('==+.*?==+', sub_str)
    if r:
        return sub_str[:r.span()[0]]
    else:
        return sub_str


def get_next(string):
    sub_str = ''
    mark = 0
    if re.match('<<<|>>>', string):
        r = re.match('[>>>|<<<].*?==+.*?==+|[>>>|<<<].*?$', string).span()
        sub_str = string[:r[1]]
        sub_str = strip_title(sub_str)
        mark = 0
    elif string.startswith('=='):
        r = re.match('==+.+?==+', string)
        if r:
            sub_str = string[:r.span()[1]]
        else:
            r = re.match('=+', string).span()
            sub_str = string[:r[1]]
        mark = 1
    else:
        r = re.match('.*?==+.*?==+|.*$', string).span()
        sub_str = string[:r[1]]
        sub_str = strip_title(sub_str)
        mark = 2
    split = len(sub_str)
    return sub_str, string[split:], mark

def get_titles(title_list):
    titles = ''
    if len(title_list):
        titles = '.'.join(title_list)+'. '*(4-len(title_list))
    else:
        titles = ' . . . '
    return titles


def output(lines, n, error_file):
    print('starting subprocess %d...'%n)
    with open(output_file + str(n)+'.txt', 'w', encoding = 'utf-8') as outfile:
        i = 0
        for line in lines:
            if i%1000==0:
                print('subprocess %d: %d finished'%(n, i))
            line_list = line.split('|')
            ID = line_list[0]
            main_title = line_list[1]
            main_title_p = len(ID) + 1
            content = line_list[2].strip()
            content_p = main_title_p + len(main_title) + 1
            title_list = []
            out_list = []
            flag = 1
            if ID.startswith('5'):
                sents = splitter(main_title)
                for s in sents.sents:
                    s = str(s)
                    temp = main_title_p + main_title.find(s)
                    out_list.append(ID+'|'+'<EMPTY_TITLE>'+'|'+s.strip()+'|'+' . . . '+'|'+str(temp))
                while(content):
                    sub, content, mark = get_next(content)
                    if not sub:
                        print('error '+ ID)
                        break
                    if mark==2:
                        sub = '>>>' + sub
                        content_p -= 3
                    content_list = re.split('>>>|<<<', sub)
                    for con in content_list[1:]:
                        content_p += 3
                        #print(con)
                        if con.strip().strip('■').strip():
                            try:
                                sents = splitter(con)
                                for s in sents.sents:
                                    s = str(s)
                                    temp = content_p + con.find(s)
                                    out_list.append(ID+'|'+'<EMPTY_TITLE>'+'|'+s.strip()+'|'+' . . . '+'|'+str(temp))
                                    #content_p += len(s)
                            except:
                                print('error '+ID)
                                flag = 0
                        content_p += len(con)

            else:
                while(content):
                    sub, content, mark = get_next(content)
                    if not sub:
                        print('error '+ ID)
                        break
                    if mark==1:
                        content_p += len(sub)
                        if sub.strip('='):
                            c = sub.count('=')/2-2
                            while(c < len(title_list)):
                                title_list.pop()
                            title_list.append(sub.strip('='))
                    else:
                        if mark==2:
                            sub = '>>>' + sub
                            content_p -= 3
                        sub_titles = get_titles(title_list)
                        content_list = re.split('>>>|<<<', sub)
                        for con in content_list[1:]:
                            content_p += 3
                            #print(con)
                            if con.strip().strip('■').strip():
                                try:
                                    sents = splitter(con)
                                    for s in sents.sents:
                                        s = str(s)
                                        temp = content_p + con.find(s)
                                        out_list.append(ID+'|'+main_title+'|'+s.strip()+'|'+sub_titles+'|'+str(temp))
                                        #content_p += len(s)
                                except:
                                    print('error '+ID)
                                    flag = 0
                            content_p += len(con)
            if out_list and flag:
                outfile.writelines('\n'.join(out_list)+'\n')
            elif not flag:
                with open(error_file, 'a+') as f: 
                    f.writelines(line)
            i+=1
        print('subprocess %d: all finished'%(n))



if __name__ == '__main__':
    if multiprocess:
        text_list = []
        n = int(math.ceil(text_length/8))
        with open(input_file) as infile:
            p_list= []
            for i in range(8):
                next_n_lines = list(islice(infile, n))
                p = Process(target=output,args=(next_n_lines, i, error_file)) 
                p.start()
                p_list.append(p)
                
            for ap in p_list:
                ap.join()
    else:
        with open(input_file) as infile:
            lines = infile.readlines()
            output(lines, 0, error_file)
