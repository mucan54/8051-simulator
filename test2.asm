

MOV R7, #6

MOV DPTR,#TAB
MOV A, #1
MOVC A, @A+DPTR


TAB: DB '0' , '1' , '2', 4,5,6,7