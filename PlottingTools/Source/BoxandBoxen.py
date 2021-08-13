from Functions import *
import DataAccessLayer as dal 
def boxwhisker_plot(mindistance,maxdistance,date=None,day=None,month=None,year=None,boxOrBoxen=2,
                        title='',filename=None,DateInterval =1,KeepData=False,ShowPlot=True,
                        DataFrame=None,Filters=None):
    startdate, enddate, title = VariableTesting(mindistance,maxdistance,date,day,month,year,title,DateInterval)
    if DataFrame is None:
        df = Queries(startdate,enddate,mindistance,maxdistance,2)
        DataFrame = df.copy(deep=True)
    else:
        df = DataFrame.copy(deep=True)
    extension = ''   
    sorter = ['u','g','r','i','z','y']
    sorterIndex = dict(zip(sorter, range(len(sorter))))    
    selection = ['mag', 'heliocentricdist','topocentricdist', 'eclipticbeta']
    units = ['H','(au)','(au)','(Degrees)']
    labels = ['Absolute Magnitude','Heliocentic Distance','Topocentric Distance', 'Ecliptic Beta Angle']
    df['numeric'] = df['filter'].map(sorterIndex)
    
    if Filters is not None:
        if Filters != 'ALL':
            extension = '-'+Filters
            check = ps.DataFrame()
            for booleanIndex in [df['filter'] == letter for letter in Filters]:
                check = ps.concat([check,df[booleanIndex]])
            df=check
        else:
            df['filter'] = 'All'
            extension = '-ALL'
            
    additiontoextension = {0:'-box',1:'-boxen',2:'-box-and-boxen'}
    extension+=additiontoextension[boxOrBoxen]
    if maxdistance >= 10:
        selection.pop(2)
        units.pop(2)
        labels.pop(2)
    if boxOrBoxen == 2 :
        fig, axes = plt.subplots(2, len(selection),figsize=(10*len(selection),20))
    else:
        fig, axes = plt.subplots(1, len(selection),figsize=(10*len(selection),10))
    for i, col in enumerate(selection):
        sns.color_palette('colorblind')
        if boxOrBoxen == 0:
            
            ax = sns.boxplot(x=df.sort_values(by='numeric')['filter'],y=df[col], ax=axes.flatten()[i])
            DoubleBox_en_Call(ax,df,i, col,labels,units)
            ax.xaxis.get_label().set_fontsize(20)
            ax.yaxis.get_label().set_fontsize(20)
            ax.set_yticks(ax.get_yticks())
            ax.set_yticklabels(ax.get_yticklabels(),fontsize=20)
            ax.set_xticks(ax.get_xticks())
            ax.set_xticklabels(ax.get_xticklabels(),fontsize=20)
            ax.tick_params(axis='both', labelsize=20)
            
        elif boxOrBoxen == 1:
            ax = sns.boxenplot(x=df.sort_values(by='numeric')['filter'],y=df[col], ax=axes.flatten()[i])
            DoubleBox_en_Call(ax,df,i, col,labels,units)
            ax.xaxis.get_label().set_fontsize(20)
            ax.yaxis.get_label().set_fontsize(20)
            ax.set_yticks(ax.get_yticks())
            ax.set_yticklabels(ax.get_yticklabels(),fontsize=20)
            ax.set_xticks(ax.get_xticks())
            ax.set_xticklabels(ax.get_xticklabels(),fontsize=20)
            ax.tick_params(axis='both', labelsize=20)
            
        elif boxOrBoxen == 2:
            ax = sns.boxplot(x=df.sort_values(by='numeric')['filter'],y=df[col], ax=axes.flatten()[i])
            
            DoubleBox_en_Call(ax,df,i, col,labels,units)
            ax.xaxis.get_label().set_fontsize(20)
            ax.yaxis.get_label().set_fontsize(20)
            ax.set_yticks(ax.get_yticks())
            #ax.set_yticklabels(ax.get_yticklabels(),fontsize=20)
            ax.set_xticks(ax.get_xticks())
            ax.set_xticklabels(ax.get_xticklabels(),fontsize=20)
            ax.tick_params(axis='both', labelsize=20)
            ax = sns.boxenplot(x=df.sort_values(by='numeric')['filter'],y=df[col], ax=axes.flatten()[len(selection)+i])
            DoubleBox_en_Call(ax,df,i, col,labels,units)
            ax.xaxis.get_label().set_fontsize(20)
            ax.yaxis.get_label().set_fontsize(20)
            ax.set_yticks(ax.get_yticks())
            #ax.set_yticklabels(ax.get_yticklabels(),fontsize=20)
            ax.set_xticks(ax.get_xticks())
            ax.set_xticklabels(ax.get_xticklabels(),fontsize=20)
            ax.tick_params(axis='both', labelsize=20)
            
    
    plt.suptitle(title+' '+str(DateorMJD(MJD=startdate)).replace('18:00:00.000','')+'- '+str(DateorMJD(MJD=float(enddate))).replace('18:00:00.000',''),size= 'xx-large',horizontalalignment='center')
    if filename is None:
        SavePlot(title+extension,dict(),ShowPlot=ShowPlot)
    else: 
        SavePlot(filename,dict(),ShowPlot=ShowPlot)
    if (KeepData == True):
        return DataFrame
    
    
    
def violin_plot(mindistance,maxdistance,date=None,day=None,month=None,year=None,boxOrBoxen=2,
                        title='',filename=None,DateInterval =1,KeepData=False,ShowPlot=True,
                        DataFrame=None,Filters=None):
    startdate, enddate, title = VariableTesting(mindistance,maxdistance,date,day,month,year,title,DateInterval)
    if DataFrame is None:
        df = Queries(startdate,enddate,mindistance,maxdistance,2)
        DataFrame = df.copy(deep=True)
    else:
        df = DataFrame.copy(deep=True)
        
    sorter = ['u','g','r','i','z','y']
    sorterIndex = dict(zip(sorter, range(len(sorter))))    
    selection = ['mag', 'heliocentricdist','topocentricdist', 'eclipticbeta']
    units = ['H','(au)','(au)','(Degrees)']
    labels = ['Absolute Magnitude','Heliocentic Distance','Topocentric Distance', 'Ecliptic Beta Angle']
    df['numeric'] = df['filter'].map(sorterIndex)
    
    if Filters is not None:
        if Filters != 'ALL':
            check = ps.DataFrame()
            for booleanIndex in [df['filter'] == letter for letter in Filters]:
                check = ps.concat([check,df[booleanIndex]])
            df=check
        else:
            df['filter'] = 'All'
            
    
    
    if maxdistance >= 10:
        selection.pop(2)
        units.pop(2)
        labels.pop(2)
    fig, axes = plt.subplots(1, len(selection),figsize=(10*len(selection),10))
    for i, col in enumerate(selection):
        sns.color_palette('colorblind')
        ax = sns.violinplot(x=df.sort_values(by='numeric')['filter'],y=df[col],bw=0.1,ax=axes.flatten()[i])
        DoubleBox_en_Call(ax,df,i, col,labels,units)
        ax.xaxis.get_label().set_fontsize(20)
        ax.yaxis.get_label().set_fontsize(20)
        ax.set_yticks(ax.get_yticks())
        #ax.set_yticklabels(ax.get_yticklabels(),fontsize=20)
        ax.set_xticks(ax.get_xticks())
        ax.set_xticklabels(ax.get_xticklabels(),fontsize=20)
        ax.tick_params(axis='both', labelsize=20)
    
    plt.suptitle(title+' '+str(DateorMJD(MJD=startdate)).replace('18:00:00.000','')+'- '+str(DateorMJD(MJD=float(enddate))).replace('18:00:00.000',''),size= 'xx-large',horizontalalignment='center')
    plt.tight_layout()
    if (filename is not None):
        SavePlot(filename, dict(),ShowPlot)
    else:
        SavePlot(title+'-violin' ,dict(),ShowPlot)
    if (KeepData == True):
        return df   

    