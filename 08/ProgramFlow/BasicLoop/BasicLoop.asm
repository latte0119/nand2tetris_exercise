@0
D=A
@SP
A=M
M=D
@SP
M=M+1
@0
D=A
@LCL
M=M+D
@SP
AM=M-1
D=M
@LCL
A=M
M=D
@0
D=A
@LCL
M=M-D
($LOOP_START)
@ARG
D=M
@0
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@LCL
D=M
@0
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
@6
M=D
@SP
AM=M-1
D=M
@5
M=D
@6
D=M
@5
M=M+D
@5
D=M
@SP
A=M
M=D
@SP
M=M+1
@0
D=A
@LCL
M=M+D
@SP
AM=M-1
D=M
@LCL
A=M
M=D
@0
D=A
@LCL
M=M-D
@ARG
D=M
@0
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
@6
M=D
@SP
AM=M-1
D=M
@5
M=D
@6
D=M
@5
M=M-D
@5
D=M
@SP
A=M
M=D
@SP
M=M+1
@0
D=A
@ARG
M=M+D
@SP
AM=M-1
D=M
@ARG
A=M
M=D
@0
D=A
@ARG
M=M-D
@ARG
D=M
@0
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
@5
M=D
@5
D=M
@$LOOP_START
D;JNE
@LCL
D=M
@0
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
