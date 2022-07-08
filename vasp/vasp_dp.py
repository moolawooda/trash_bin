import os
import pandas


'''
函数名称：file_open
函数功能：打开指定文件，并按行转换成嵌套列表形式
输入变量：
    file_name：文件名
输出变量：
    raw_data：未经处理的数据
'''
def file_open(file_name):
    file = open(file_name, encoding='utf-8')
    lines = file.read().split("\n")
    raw_data = []

    for line in lines:
        objects = line.split(' ')
        if objects[0] != '':
            raw_data.append(objects)

    return raw_data


'''
函数名称：direction_list
函数功能：从raw_data中读取晶向列表
输入变量：
    raw_data：未经处理的数据
输出变量：
    direction_list：晶向列表
'''
def get_direction_list(raw_data):
    direction_list = []
    for item in raw_data:
        if item[1] not in direction_list:
            direction_list.append(item[1])

    direction_list.sort(key=lambda x:(int(x)))
    return direction_list


'''
函数名称：data_management
函数功能：从raw_data中读取数据，删除无用信息，添加位移为0的数据，并且排序
输入变量：
    raw_data：未经处理的数据
    direction_list：晶向列表
    file_type：文件类型，用于确定处理方式
输出变量：
    pre_processed_data：预处理后的数据
'''
def data_management(raw_data,direction_list,file_type):
    pre_processed_data = []
    if file_type == 'band':
        for item in raw_data:
            if item[2] != '0':
                pre_processed_data.append([item[0],item[1],item[2],item[-1]])
            else:
                for direction in direction_list:                   
                    pre_processed_data.append([item[0],direction,item[2],item[-1]])

    elif file_type == 'pes':
        for item in raw_data:        
            if item[2] != '0':
                pre_processed_data.append([item[0],item[1],item[2],item[-5]])
            else:
                for direction in direction_list:                   
                    pre_processed_data.append([item[0],direction,item[2],item[-5]])

    pre_processed_data.sort(key=lambda x:(int(x[1]),float(x[0]),int(x[2])))
    return pre_processed_data


'''
函数名称：get_list
函数功能：从pre_processed_data中读取数据，得到各个列表
输入变量：
    pre_processed_data：预处理后的数据
输出变量：
    a_list：晶胞参数列表
    displacement_list：偏心距离列表
'''
def get_list(pre_processed_data):
    a_list = []
    displacement_list = []

    for item in pre_processed_data:
        if item[0] not in a_list:
            a_list.append(item[0])
        if item[2] not in displacement_list:
            displacement_list.append(item[2])

    return a_list, displacement_list   


'''
函数名称：contour_generation
函数功能：从pre_processed_data中读取数据，得到等高线图格式的数据
输入变量：
    pre_processed_data：预处理后的数据
    step_size：步长
    a_list：晶胞参数列表
    direction_list：晶向列表
    displacement_list：偏心距离列表
输出变量：
    contour：等高线图数据
'''
def contour_generation(pre_processed_data,step_size,a_list,direction_list,displacement_list):
    contour = [['a','Displacement'],['A', str(step_size)+' A'],['','']]

    for direction in direction_list:
        contour[0].append("Band Gap")
        contour[1].append("eV")
        contour[2].append(direction)

    i = 0
    for item in pre_processed_data:
        if item[1] == '100':
            contour.append([item[0],item[2],item[3]])
        else:
            if item[1] == '110':
                val = 209
            else:
                val = 418
            contour[i-val+3].append(item[3])
        i = i + 1
    return contour


'''
函数名称：plot_generation
函数功能：从pre_processed_data中读取数据，得到点线图格式的数据
输入变量：
    pre_processed_data：预处理后的数据
    step_size：步长
    a_list：晶胞参数列表
    direction_list：晶向列表
    displacement_list：偏心距离列表
    file_type：文件类型，用于确定处理方式
输出变量：
    plot_list：点线图数据
'''
def plot_generation(pre_processed_data,step_size,a_list,direction_list,displacement_list,file_type):
    plot = [['Displacement'],[str(step_size) + ' A'],['']]
    plot_list = []

    for a in a_list:
        if file_type == "band":
            plot[0].append('Band Gap')
        elif file_type == "pes":
            plot[0].append('E-E0')
        plot[1].append('eV')
        plot[2].append(a)

    for displacement in displacement_list:
        plot.append([displacement])

    for direction in direction_list:
        plot_dir = plot[:]
        for item in pre_processed_data:
            if item[1] == direction:
                plot_dir[int(item[2])+3].append(item[3])

        plot_int = []
        for item in plot_dir:
            plot_int.append(item[:len(a_list)+1])
        plot_list.append(plot_int)

    return plot_list


'''
函数名称：pes_substraction
函数功能：从plot_list中读取数据，减去无偏心时的能量，得到pes的点线图格式的数据
输入变量：
    plot_list：点线图数据
    direction_list：晶向列表
输出变量：
    pes_list：pes的点线图数据（相对能量）
'''
def pes_substraction(plot_list,direction_list):
    pes_list = []
    for pes in plot_list:
        pes_0 = pes[3]
        pes_exp = pes[:3]
        i = 0
        for items in pes[3:]:
            pes_exp.append([])
            j = 0
            for item in items:
                pes_exp[i+3].append(round(float(pes[i+3][j]) - float(pes_0[j]), 10))
                j = j+1
            i = i+1
        pes_list.append(pes_exp)
    return pes_list


'''
函数名称：file_save
函数功能：保存数据，输出到文件
输入变量：
    data_sets：准备保存的数据
    data_type：数据类型（是否嵌套）
    file_name：文件名
    direction_list：晶向列表
输出变量：
    *.csv：输出到csv文件
'''
def save_file(data_sets,data_type,file_name,direction_list):
    if data_type == 'multi':
        i = 0
        for data_set in data_sets:
            data = pandas.DataFrame(data=data_set)
            save_name = "./" + file_name[:-4] + "_" + direction_list[i] + ".csv"
            data.to_csv(save_name, encoding='utf-8', header=0, index=0)
            i = i + 1
    elif data_type == 'single':
        data = pandas.DataFrame(data=data_sets)
        save_name = "./" + file_name[:-4] + ".csv"
        data.to_csv(save_name, encoding='utf-8', header=0, index=0)


'''
函数名称：to_band
函数功能：保存band数据，输出到文件
输入变量：
    file_name：文件名
    step_size：步长
输出变量：
    *.csv：输出到csv文件
'''
def to_band(file_name,step_size):

    file_type = 'band'
    raw_data = file_open(file_name)
    direction_list = get_direction_list(raw_data)
    pre_processed_data = data_management(raw_data, direction_list, file_type)
    a_list,displacement_list = get_list(pre_processed_data)    

    contour = contour_generation(pre_processed_data, step_size, a_list, direction_list, displacement_list)
    plot_list = plot_generation(pre_processed_data, step_size, a_list, direction_list, displacement_list, file_type)

    save_file(contour, 'single', file_name, direction_list)
    save_file(plot_list, 'multi', file_name, direction_list)


'''
函数名称：to_pes
函数功能：保存pes数据，输出到文件
输入变量：
    file_name：文件名
    step_size：步长
输出变量：
    *.csv：输出到csv文件
'''
def to_pes(file_name,step_size):

    file_type = 'pes'
    raw_data = file_open(file_name)
    direction_list = get_direction_list(raw_data)
    pre_processed_data = data_management(raw_data, direction_list, file_type)
    a_list,displacement_list = get_list(pre_processed_data)    

    plot_list = plot_generation(pre_processed_data, step_size, a_list, direction_list, displacement_list, file_type)
    pes_list = pes_substraction(plot_list, direction_list)

    save_file(pes_list, 'multi', file_name, direction_list)


'''
函数名称：auto_run
函数功能：自动检测目录下所有的.out文件，并自动转换成.csv格式的输出文件
输入变量：
    step_size：步长
输出变量：
    *.csv：输出到csv文件
'''
def auto_run(step_size):
    files = os.listdir("./")
    for file in files:
        file_name = file
        if ".out" in file:
            if "Band" in file:
                to_band(file_name, step_size)
            elif "PES" in file:
                to_pes(file_name, step_size)    


# 本程序会自动检测目录下所有的.out文件，并自动转换成.csv格式的输出文件，
# 唯一需要指定的参数是步长，其余参数会自动从文件中读取。
step_size = 0.06
auto_run(step_size)
