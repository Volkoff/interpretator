; ModuleID = "oberon_module"
declare i32 @printf(i8*, ...)

define i32 @main() {
entry:
  %message = alloca i8*
  %t1 = getelementptr inbounds [14 x i8], [14 x i8]* @.str1, i32 0, i32 0
  store i8* %t1, i8** %message
  %t2 = load i8*, i8** %message
  %t3 = getelementptr inbounds [3 x i8], [3 x i8]* @.str2, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t3, i8* %t2)
  %t4 = getelementptr inbounds [2 x i8], [2 x i8]* @.str3, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t4)
  ret i32 0
}

@.str1 = private constant [14 x i8] c"Hello, World!\00"
@.str2 = private constant [3 x i8] c"%s\00"
@.str3 = private constant [2 x i8] c"\0A\00"