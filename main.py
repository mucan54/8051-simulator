import re
import sys  
from io import BytesIO


#work([['P1',0]],'/Users/mucan/Documents/hys.asm',200)

def getv(c):
    val=[]
    if(c.find(':')!=-1):
        i=c.find(':')
        while(c[i]==' '):
            i=+1       
        c=c[c.find(':')+i:len(c)]
    sp=c.find(' ')
    c=c[sp:len(c)].replace(" ", "")
    while True:
        if(c.find(',')!=-1):
            s=c[0:c.find(',')]
            val.append(s)
            c=c[c.find(',')+1:len(c)]
        else:
            val.append(c)
            break
        
    return val
       
# this always return a int value
def convert(item):
    if(str(item).find('#')!=-1):  # remove the beginning #
        item=item[1:len(item)]
    
    if(str(item).find('H')!=-1):
        item=item[0:len(item)-1]
        return int(item, 16)
    if(str(item).find('B')!=-1):
        item=item[0:len(item)-1]
        return int(item, 2)
    if(str(item).find('D')!=-1):
        item=item[0:len(item)-1]
        return int(item)
    else:
        return int(item)


def mov_v(s1, memd):
    if(s1 in memd):
        va=memd.index(s1)
        return mem[va][1]
    else:
        return 0

def mov_check(s2, memd,a):
    s2=str(s2)
 
    if(s2.find('@')==-1):
        if(s2.find('#')!=-1 and a==2):
            return convert(s2)
        else:
            if a==1:
                if(s2[len(s2)-1]=='H'):
                    s2=s2[0:len(s2)-1]
                return s2
            elif a==2:
                return mov_v(s2,memd)
    else:
        s2=s2[1:len(s2)]
        s2=mov_v(s2, memd)
        if(a==1):
            return s2
        else:
            return convert(mov_v(s2, memd))
    

def mov_d(s1, s2, memd):
    if(s1 in memd):
       va=memd.index(s1)
       mem[va]=[mem[va][0],s2]
    else:
       mem.append([s1,s2])


def work(mem2,file, y):
    global mem
    mem=[]
    memd=[]
    if mem2!='':
        mem.append(mem2)
    with open(file, 'r', encoding="utf-8") as f:
        content=f.readlines()
    content = [x.strip().upper() for x in content]
    loop=len(content)
    x=0
    x_wt=y
    x_crnt=0
    while x < loop:
        if(x_crnt<x_wt):
            x_crnt=x_crnt+1
        else:
            print(mem)
            break
        memd=[]
        item=content[x]
        memd=[a[0] for a in mem]
        if(item.find('MOV')!=-1 and item.find('MOVC')==-1):
            if(item.find('DPTR')==-1):
                val=getv(item)
                val[0]=mov_check(val[0],memd,1)
                val[1]=mov_check(val[1],memd,2)
                mov_d(val[0],convert(val[1]),memd)
            else:
                mov_d('DPTR', item[item.find('#')+1:len(item)],memd)
        if(item.find('ADD')!=-1):
            val=getv(item)
            val[1]=mov_check(val[1],memd,2)
            val[0]=mov_check(val[0],memd,1)
            if(mov_v(val[0],memd)+val[1]<=255):
                mov_d(val[0],mov_v(val[0],memd)+val[1],memd)
            else:
                mov_d(val[0],255,memd)
                mov_d('C',1,memd)
        if(item.find('INC')!=-1):
            val=getv(item)
            mov_d(val[0],int(mov_v(val[0],memd))+1,memd)
        if(item.find('DB')!=-1):       
            mov_d(item[0:item.find(':')],getv(item[10:len(content[0])]),memd)

        if(item.find('JZ')!=-1):
            val=getv(item)
            if(mov_d('A')==0):
                x=content.index(val[1]+':')

        if(item.find('JNZ')!=-1):
            val=getv(item)
            if(mov_v('A',memd)!=0):
                x=content.index(val[1]+':')

        if(item.find('JC')!=-1):
            val=getv(item)
            if(mov_d('C')!=0):
                x=content.index(val[1]+':')

        if(item.find('JNC')!=-1):
            val=getv(item)
            if(mov_v('C',memd)==0):
                x=content.index(val[1]+':')
            
        if(item.find('SJMP')!=-1):
            item=item.replace(" ", "")
            x=content.index(item[4:len(item)]+':')

        if(item.find('DJNZ')!=-1):
            val=getv(item)
            if(int(mov_v(val[0],memd))-1>0):
                mov_d(val[0],int(mov_v(val[0],memd))-1,memd)
                x=content.index(val[1]+':')
            else:
                mov_d(val[0],int(mov_v(val[0],memd))-1,memd)

        if(item.find('SETB')!=-1):
            val=getv(item)
            s=val[0]
            s=int(s[s.find('.')+1])
            s=2**s
            b=mov_v(val[0][0:val[0].find('.')],memd)
            nv=s|int(b)
            mov_d(val[0][0:val[0].find('.')],nv,memd)


        if(item.find('CLR')!=-1):
            val=getv(item)
            s=val[0]
            if(s.find('.')!=-1):
                b=mov_v(s[0:s.find('.')],memd)
                s=int(s[s.find('.')+1])
                b=bin(b)
                nv=b[0:len(b)-1-s]+'0'+b[len(b)-s:len(b)]
                nv=int(nv,2)
                mov_d(val[0][0:val[0].find('.')],nv,memd)
            else:
                mov_d(val[0],'0',memd)
        
        if(item.find('CJNE')!=-1):
            val=getv(item)
            val[0]=mov_check(val[0],memd,2)
            val[1]=mov_check(val[1],memd,2)
            if(val[0]!=val[1]):
                x=content.index(val[2]+':')

        if(item.find('SWAP')!=-1):
            val=getv(item)
            b=mov_v(val[0],memd)
            b=hex(int(b))
            if(len(b)==3):
                b='0x0'+str(b[2])
            c='0x'+str(b[len(b)-1])+str(b[len(b)-2])
            c=int(c, 16)
            mov_d(val[0],c,memd)
                
        if(item.find('XCHD')!=-1):
            val=getv(item)
            s1=mov_check(val[0],memd,1)
            s2=mov_check(val[1],memd,2)
            s1=hex(int(mov_v(s1,memd)))
            s2=hex(int(s2))
            if(len(s2)==3):
                s2='0x0'+str(s2[2])
            if(len(s1)==3):
                s1='0x0'+str(s1[2])
            b1='0x'+str(s1[len(s1)-2])+str(s2[len(s2)-1])
            b2='0x'+str(s2[len(s2)-2])+str(s1[len(s1)-1])
            mov_d(mov_check(val[0],memd,1),int(b1, 16),memd)
            mov_d(mov_check(val[1],memd,1),int(b2, 16),memd)

        if(item.find('MOVC')!=-1 and item.find('DPTR')!=-1):
            if(item.find('DPTR')!=-1 and item.find('@A')!=-1):
                a=(mov_v(mov_v('DPTR',memd),memd))
                b=mov_v('A',memd)
                mov_d('A',a[b],memd)

        if(item.find('MUL AB')!=-1):
            s1=mov_check('A',memd,2)
            s2=mov_check('B',memd,2)
            mul=int(s1)*int(s2)
            if(mul>255):
                mov_d('OV',1,memd)
            mul=hex(mul)
            mul=mul[2:len(x)]
            while(len(x)<4):
                mul='0'+mul
            s2='0x'+mul[0:2]
            s1='0x'+mul[2:4]
            
            mov_d('C',0,memd)
            mov_d('A',int(s2, 16),memd)
            mov_d('B',int(s1, 16),memd)

        if(item.find('SUBB')!=-1):
            val=getv(item)
            s1=mov_check(val[0],memd,2)
            s2=mov_check(val[1],memd,2)
            if(s1>=s2):
                mov_d('A',s1-s2,memd)
            else:
                s3=bin(s2-s1)
                x=len(s3)
                while(x>1):
                    if(s3[x]=='1'):
                        y=y+'0'
                    else:
                        y=y+'1'

                y='0b'+y
            mov_d('C',1,memd)                
            mov_d('A',int(y,2),memd)               

        if(item.find('DIV AB')!=-1):
            s1=mov_check('A',memd,2)
            s2=mov_check('B',memd,2)
            mov_d('A',int(s1/s2),memd)
            mov_d('B',int(s1%s2),memd)

        x+=1
    print(mem)
        

    
