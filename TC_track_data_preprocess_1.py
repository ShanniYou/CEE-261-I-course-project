from file_1.GEOS5functions import *
from metpy.units import units
from metpy.interpolate import log_interpolate_1d
#matplotlib.use('Agg')
import cartopy.crs as ccrs


def main():
    #all_data1,tctime1,all_data2,tctime2 = loop_storm()
    filename_cane = loop_storm()
    variable_name = ['all_data1','tctime1','all_data2','tctime2']
    #print(all_data1,tctime1.shape,all_data2.shape,tctime2.shape)
    fill_files(filename_cane,variable_name)

    file_list = ['all_data1','all_data2','tctime1','tctime2']
    all_data1,all_data2,tctime1,tctime2 = loading(file_list)

    print(all_data1.shape, tctime1, all_data2.shape, tctime2.shape)

def loading(file_list):
    all_data1 = []
    all_data2 = []
    tctime1 = []
    tctime2 = []
    idx = 0
    for filename in file_list:
        print(filename)
        str ='track_data' + '\\' + filename + '.txt'
        f = open(str,'r')
        line = f.readline()
        while line:
            if idx == 0:
                all_data1.append(line)
            elif idx ==1:
                all_data2.append(line)
            elif idx ==2:
                    #print(inlines)
                tctime1.append(line)
            elif idx ==3:
                tctime2.append(line)
            line = f.readline()
        idx += 1
        f.close()
    length = int(all_data1[-1])
    dshape1 = ((2,int(length)))
    dshape2 = ((6,int(length)))
    print(dshape1)
    data1 = np.empty(dshape2,dtype=np.dtype(np.float64))
    data2 = np.empty(dshape2,dtype=np.dtype(np.float64))
    time1 = np.empty(dshape1,dtype="S16")
    time2 = np.empty(dshape1,dtype="S16")
    all_data1 = map(lambda x: np.float(x), all_data1)
    all_data2 = map(lambda x: np.float(x), all_data2)
    all_data1 = np.array(list(all_data1))
    all_data2 = np.array(list(all_data2))
    for i in range(data1.shape[0]):

        data1[i,:] = all_data1[i*length:(i+1)*length]
        data2[i, :] = all_data2[i * length:(i + 1) * length]

    for j in range(time1.shape[0]):
        time1[j,:] = tctime1[j*length:(j+1)*length]
        time2[j, :] = tctime2[j * length:(j + 1) * length]

    return data1,data2,time1,time2


def loop_storm():
    stormlist = getallstorms()
    storm_exist_name = get_storm_npz_list()
    Tctime1 = None
    Minplon1 = None
    Minplat1 = None
    Minpres1 = None

    Tctime2 = None
    Minplon2 = None
    Minplat2 = None
    Minpres2 = None
    for i in range(170):
        currentstorm = i
        name = str(stormlist[1][currentstorm][:-1])
        if name in storm_exist_name:
            stormname = name
            tctime,minplon,minplat,minpres = get_center(stormname)
            N = tctime.shape[0]
            stctime = map(lambda x: np.str(x)[0:16],np.array(tctime))
            stctime = np.array(list(stctime))
            length = stctime.shape[0]

            if int(length)%2 != 0:
                length = length-1

            stctime_double = np.vstack((stctime[0:length-48],stctime[48:length]))
            minplon_double = np.vstack((minplon[0:length-48], minplon[48:length]))
            minplat_double = np.vstack((minplat[0:length-48], minplat[48:length]))
            minpres_double = np.vstack((minpres[0:length-48], minpres[48:length]))

            stctime1,stctime2 = np.hsplit(stctime_double,2)
            minplon1,minplon2 = np.hsplit(minplon_double,2)
            minplat1,minplat2 = np.hsplit(minplat_double,2)
            minpres1,minpres2 = np.hsplit(minpres_double,2)

            if Tctime1 is None:
                Tctime1 = stctime1
                Minplon1 = minplon1
                Minplat1 = minplat1
                Minpres1 = minpres1

                Tctime2 = stctime2
                Minplon2 = minplon2
                Minplat2 = minplat2
                Minpres2 = minpres2
            else:
                Tctime1 = np.hstack((Tctime1,stctime1))
                Minplon1 = np.hstack((Minplon1,minplon1))
                Minplat1 = np.hstack((Minplat1,minplat1))
                Minpres1 = np.hstack((Minpres1,minpres1))

                Tctime2 = np.hstack((Tctime2, stctime2))
                Minplon2 = np.hstack((Minplon2, minplon2))
                Minplat2 = np.hstack((Minplat2, minplat2))
                Minpres2 = np.hstack((Minpres2, minpres2))
        else:
            print(name,'does not exists')

    ALL_data1 = np.empty((6,Tctime1.shape[1]))
    #print(Minplon1.shape)
    ALL_data1[0:2,:] = Minplon1
    ALL_data1[2:4,:] = Minplat1
    ALL_data1[4:6,:] = Minpres1

    ALL_data2 = np.empty((6, Tctime2.shape[1]))
    ALL_data2[0:2, :] = Minplon2
    ALL_data2[2:4, :] = Minplat2
    ALL_data2[4:6, :] = Minpres2
    return ALL_data1,Tctime1,ALL_data2,Tctime2



def get_center(stormname):
    npzfile = np.load('data\\' + stormname[0:9] + '.npz')
    tctime = npzfile['time']
    minplon = npzfile['minplon']
    minplat = npzfile['minplat']
    minpres = npzfile['minpres']
    return tctime,minplon,minplat,minpres



def get_storm_npz_list():
    f = open(r'data\npz_list.txt')
    line = f.readline()
    storm_name = []
    while line:
        line = line.strip('\n')
        num = line.split()
        for n in num:
            storm_name.append(n[:-4])
        line = f.readline()
    f.close()
    return np.array(storm_name)



def fill_files(file_cane,variable_name):
    idx =0

    for file in file_cane:
        length = []
        length.append(file.shape[1])

        str = 'track_data' + '\\' + variable_name[idx] + '.txt'
        f = open(str,'w')
        for i in range(file.shape[0]):
            line = file[i,:]
            np.savetxt(f,line,fmt='%s')
        np.savetxt(f,np.array(length),fmt = '%s')
        f.close()
        idx+=1


if __name__ == '__main__':
    main()










