; ModuleID = "oberon_module"
declare i32 @printf(i8*, ...)

define i32 @main() {
entry:
  %x = alloca i32
  store i32 42, i32* %x
  %t1 = load i32, i32* %x
  %t2 = getelementptr inbounds [3 x i8], [3 x i8]* @.str1, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t2, i32 %t1)
  ret i32 0
}

@.str1 = private constant [3 x i8] c"%d\00"