from file_1.GEOS5functions import *
from metpy.units import units
from metpy.interpolate import log_interpolate_1d
#matplotlib.use('Agg')
import cartopy.crs as ccrs


def main():
    # data preprocessing:
    # data_preprocess()

    # for the drawing part

    file_list = ['x_train_0','x_train_1','y_train_0','y_train_1','y_lon','y_lat']
    x_train_0 = reading_result(file_list[0])
    x_train_1 = reading_result(file_list[1])
    y_train_0 = reading_result(file_list[2])
    y_train_1 = reading_result(file_list[3])
    y_lon = reading_result(file_list[4])
    y_lat = reading_result(file_list[5])
    print(x_train_0)
    print(x_train_1)
    print(y_train_0)
    print(y_train_1)
    print(y_lon)
    print(y_lat)

    fig = plt.figure(figsize=(80, 40))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.scatter(x_train_0[:-1], x_train_1[:-1], label='original_track_0h',marker = 'x', c = 'b' , s = 100)
    ax.scatter(y_train_0[:-1], y_train_1[:-1], label='exactly_track_24h_later',marker = '3', c = 'g' , s = 100)

    ax.scatter(y_lon[:-1], y_lat[:-1], label='predict_track_24h_later',marker = '*', c = 'm' , s = 100)
    ax.stock_img()
    ax.coastlines()
    ax.coastlines('50m', edgecolor='white')

    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                      linewidth=2, color='gray', alpha=0.5, linestyle='--')

    plt.legend(loc=0,prop = {'size':50})
    plt.xlabel('lontitude')
    plt.ylabel('latitude')
    plt.savefig('best_model_1.png')





def data_preprocess():
    #all_data1,tctime1,all_data2,tctime2 = loop_storm()
    filename_cane = loop_storm()
    variable_name = ['all_data1','tctime1','all_data2','tctime2']
    #print(all_data1,tctime1.shape,all_data2.shape,tctime2.shape)
    fill_files(filename_cane,variable_name)

    file_list = ['all_data1','all_data2','tctime1','tctime2']
    all_data1,all_data2,tctime1,tctime2 = loading(file_list)

    print(all_data1.shape, tctime1, all_data2.shape, tctime2.shape)

def reading_result(filename):
    str = 'track_data' + '\\' + '01' + '\\' + filename + '.txt'
    f = open(str, 'r')
    line = f.readline()
    array = []
    while line:
        line = line.strip('\n')
        array.append(float(line))
        line = f.readline()
    f.close()
    return np.array(array)




def loading(file_list):
    all_data1 = []
    all_data2 = []
    tctime1 = []
    tctime2 = []
    idx = 0
    for filename in file_list:
        print(filename)
        str ='track_data' + '\\' + '01' +'\\' + filename + '.txt'
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
    length_1 = int(all_data1[-1])
    length_2 = int(all_data2[-1])
    dshape11 = ((2,int(length_1)))
    dshape12 = ((6,int(length_1)))
    dshape21 = ((2,int(length_2)))
    dshape22 = ((6,int(length_2)))

    data1 = np.empty(dshape12,dtype=np.dtype(np.float64))
    data2 = np.empty(dshape22,dtype=np.dtype(np.float64))
    time1 = np.empty(dshape11,dtype="S16")
    time2 = np.empty(dshape21,dtype="S16")
    all_data1 = map(lambda x: np.float(x), all_data1)
    all_data2 = map(lambda x: np.float(x), all_data2)
    all_data1 = np.array(list(all_data1))
    all_data2 = np.array(list(all_data2))
    for i in range(data1.shape[0]):

        data1[i,:] = all_data1[i*length_1:(i+1)*length_1]
        data2[i, :] = all_data2[i * length_2:(i + 1) * length_2]

    for j in range(time1.shape[0]):
        time1[j,:] = tctime1[j*length_1:(j+1)*length_1]
        time2[j, :] = tctime2[j * length_2:(j + 1) * length_2]

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

            valid = [20,40,60,80,100,120,140,160]
            if i in valid:
                stctime2 = stctime_double
                minplon2 = minplon_double
                minplat2 = minplat_double
                minpres2 = minpres_double

                if Tctime2 is None:

                    Tctime2 = stctime2
                    Minplon2 = minplon2
                    Minplat2 = minplat2
                    Minpres2 = minpres2
                else:

                    Tctime2 = np.hstack((Tctime2, stctime2))
                    Minplon2 = np.hstack((Minplon2, minplon2))
                    Minplat2 = np.hstack((Minplat2, minplat2))
                    Minpres2 = np.hstack((Minpres2, minpres2))

            else:
                stctime1 = stctime_double
                minplon1 = minplon_double
                minplat1 = minplat_double
                minpres1 = minpres_double

                if Tctime1 is None:
                    Tctime1 = stctime1
                    Minplon1 = minplon1
                    Minplat1 = minplat1
                    Minpres1 = minpres1

                else:
                    Tctime1 = np.hstack((Tctime1, stctime1))
                    Minplon1 = np.hstack((Minplon1, minplon1))
                    Minplat1 = np.hstack((Minplat1, minplat1))
                    Minpres1 = np.hstack((Minpres1, minpres1))



            #stctime1,stctime2 = np.hsplit(stctime_double,2)
            #minplon1,minplon2 = np.hsplit(minplon_double,2)
            #minplat1,minplat2 = np.hsplit(minplat_double,2)
            #minpres1,minpres2 = np.hsplit(minpres_double,2)


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










