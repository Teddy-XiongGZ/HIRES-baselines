from DeletePattern import DeletePattern, DeleteSpecificType
from DeleteBigWords import DeleteBigWords
from RemoveUp import RemoveUp
import pandas as pd
import re
from multiprocessing import Process

input_file = '../data/general_clean_disodiso_pred2_'
output_file1 = '../data/disodiso_pred_ups_remain'
exception1 = '../data/disodiso_pred_ups_delete'
output_file2 = '../data/disodiso_pred_bigword_remain'
exception2 = '../data/disodiso_pred_bigword_delete'
output_file3 = '../data/disodiso_pred_type_remain'
exception3 = '../data/disodiso_pred_type_delete'
output_file4 = '../data/further_clean_disodiso_pred_'
exception4 = '../data/disodiso_pred_pattern_delete'

nearpardic_file = '../data/nearpardic.txt'
neardic_file = '../data/neardic.txt'
nearrbdic_file = '../data/nearrbdic.txt'

todelete = pd.read_csv('../data/timesafter.csv')
bigword_todelete = list(todelete['cui'])

pattern_same = re.compile('t[0-9][0-9][0-9] \( t[0-9][0-9][0-9] \)')
type_todelete = ['t049', 't033', 't050', 't019']

def remove(index):
    print('removing ups...')
    upremover = RemoveUp(input_file+str(index)+'.txt', output_file1+str(index)+'.txt', exception1+str(index)+'.txt')
    upremover.init(nearpardic_file, nearrbdic_file, neardic_file)
    cnt = upremover.process()
    print('done')
    print('%d ups removed'%cnt)

    print('removing bigwords...')
    bigword_remover = DeleteBigWords(output_file1+str(index)+'.txt', output_file2+str(index)+'.txt', exception2+str(index)+'.txt', bigword_todelete)
    cnt = bigword_remover.process()
    print('done')
    print('%d big words removed'%cnt)

    print('removing type...')
    type_remover = DeleteSpecificType(output_file2+str(index)+'.txt', output_file3+str(index)+'.txt', exception3+str(index)+'.txt', type_todelete)
    cnt = type_remover.process()
    print('done')
    print('%d types removed'%cnt)

    print('removing pattern...')
    pattern_remover = DeletePattern(output_file3+str(index)+'.txt', output_file4+str(index)+'.txt', exception4+str(index)+'.txt', pattern_same)
    cnt = pattern_remover.process()
    print('done')
    print('%d patterns removed'%cnt)

if __name__ == '__main__':

    plist = []
    for i in range(9):
        p = Process(target=remove,args = (i,))
        p.start()
        plist.append(p)
    for ap in plist:
        ap.join()