MAIN:
        MOV 23,     #45H
        MOV 21H,    #45H
        MOV R1,     #62
        MOV @R1,    #23
        MOV A,      #0
LOOP:
        ADD A,      #1
        DJNZ R1,    LOOP
        PUSH A
        POP B