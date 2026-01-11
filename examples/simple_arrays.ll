; ModuleID = "oberon_module"
declare i32 @printf(i8*, ...)

define i32 @main() {
entry:
  %numbers = alloca [5 x i32], align 8
  %i = alloca i32
  %sum = alloca i32
  %t1 = getelementptr inbounds [5 x i32], [5 x i32]* %numbers, i32 0, i32 0
  store i32 1, i32* %t1
  %t2 = getelementptr inbounds [5 x i32], [5 x i32]* %numbers, i32 0, i32 1
  store i32 2, i32* %t2
  %t3 = getelementptr inbounds [5 x i32], [5 x i32]* %numbers, i32 0, i32 2
  store i32 3, i32* %t3
  %t4 = getelementptr inbounds [5 x i32], [5 x i32]* %numbers, i32 0, i32 3
  store i32 4, i32* %t4
  %t5 = getelementptr inbounds [5 x i32], [5 x i32]* %numbers, i32 0, i32 4
  store i32 5, i32* %t5
  store i32 0, i32* %sum
  store i32 0, i32* %i
  br label %for_start1
for_start1:
  %t6 = load i32, i32* %i
  %t7 = icmp sle i32 %t6, 4
  br i1 %t7, label %for_body2, label %for_end3
for_body2:
  %t8 = load i32, i32* %sum
  %t9 = load i32, i32* %i
  %t10 = getelementptr inbounds [5 x i32], [5 x i32]* %numbers, i32 0, i32 %t9
  %t11 = load i32, i32* %t10
  %t12 = add i32 %t8, %t11
  store i32 %t12, i32* %sum
  %t13 = add i32 %t6, 1
  store i32 %t13, i32* %i
  br label %for_start1
for_end3:
  %t14 = getelementptr inbounds [24 x i8], [24 x i8]* @.str1, i32 0, i32 0
  %t15 = getelementptr inbounds [3 x i8], [3 x i8]* @.str2, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t15, i8* %t14)
  %t16 = load i32, i32* %sum
  %t17 = getelementptr inbounds [3 x i8], [3 x i8]* @.str3, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t17, i32 %t16)
  %t18 = getelementptr inbounds [2 x i8], [2 x i8]* @.str4, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t18)
  ret i32 0
}

@.str1 = private constant [24 x i8] c"Sum of array elements: \00"
@.str2 = private constant [3 x i8] c"%s\00"
@.str3 = private constant [3 x i8] c"%d\00"
@.str4 = private constant [2 x i8] c"\0A\00"