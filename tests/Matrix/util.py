import re

def read_answer_file(filename):
    content = open(filename).read()
    content = re.sub('\s+', ',', content)
    return eval(content)

def read_mem_result_file(filename, target):
    for line in open(filename).readlines():
        if line.startswith(target):
            content = line.split('|')[1]
            content = re.sub('[{}]+', '', content)
            return eval(content)
    return []

def read_array_result_file(filename):
    result = []
    for line in open(filename).readlines():
        if line.startswith('row_vec'):
            content = line.split('|')[1]
            content = re.sub('[{}]+', '', content)
            result.extend(eval(content))
    return result
