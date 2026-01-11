; ModuleID = "oberon_module"
declare i32 @printf(i8*, ...)

define i32 @main() {
entry:
  %matrix = alloca [3 x [4 x i32]], align 8
  %i = alloca i32
  %j = alloca i32
  %sum = alloca i32
  store i32 0, i32* %i
  br label %for_start1
for_start1:
  %t1 = load i32, i32* %i
  %t2 = icmp sle i32 %t1, 2
  br i1 %t2, label %for_body2, label %for_end3
for_body2:
  store i32 0, i32* %j
  br label %for_start4
for_start4:
  %t3 = load i32, i32* %j
  %t4 = icmp sle i32 %t3, 3
  br i1 %t4, label %for_body5, label %for_end6
for_body5:
  %t5 = load i32, i32* %i
  %t6 = mul i32 %t5, 10
  %t7 = load i32, i32* %j
  %t8 = add i32 %t6, %t7
  %t9 = load i32, i32* %i
  %t10 = load i32, i32* %j
  %t11 = getelementptr inbounds [3 x [4 x i32]], [3 x [4 x i32]]* %matrix, i32 0, i32 %t9, i32 %t10
  store i32 %t8, i32* %t11
  %t12 = add i32 %t3, 1
  store i32 %t12, i32* %j
  br label %for_start4
for_end6:
  %t13 = add i32 %t1, 1
  store i32 %t13, i32* %i
  br label %for_start1
for_end3:
  %t14 = getelementptr inbounds [17 x i8], [17 x i8]* @.str1, i32 0, i32 0
  %t15 = getelementptr inbounds [3 x i8], [3 x i8]* @.str2, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t15, i8* %t14)
  %t16 = getelementptr inbounds [2 x i8], [2 x i8]* @.str3, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t16)
  store i32 0, i32* %i
  br label %for_start7
for_start7:
  %t17 = load i32, i32* %i
  %t18 = icmp sle i32 %t17, 2
  br i1 %t18, label %for_body8, label %for_end9
for_body8:
  store i32 0, i32* %j
  br label %for_start10
for_start10:
  %t19 = load i32, i32* %j
  %t20 = icmp sle i32 %t19, 3
  br i1 %t20, label %for_body11, label %for_end12
for_body11:
  %t21 = load i32, i32* %i
  %t22 = load i32, i32* %j
  %t23 = getelementptr inbounds [3 x [4 x i32]], [3 x [4 x i32]]* %matrix, i32 0, i32 %t21, i32 %t22
  %t24 = load i32, i32* %t23
  %t25 = getelementptr inbounds [3 x i8], [3 x i8]* @.str4, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t25, i32 %t24)
  %t26 = getelementptr inbounds [2 x i8], [2 x i8]* @.str5, i32 0, i32 0
  %t27 = getelementptr inbounds [3 x i8], [3 x i8]* @.str2, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t27, i8* %t26)
  %t28 = add i32 %t19, 1
  store i32 %t28, i32* %j
  br label %for_start10
for_end12:
  %t29 = getelementptr inbounds [2 x i8], [2 x i8]* @.str3, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t29)
  %t30 = add i32 %t17, 1
  store i32 %t30, i32* %i
  br label %for_start7
for_end9:
  store i32 0, i32* %sum
  store i32 0, i32* %i
  br label %for_start13
for_start13:
  %t31 = load i32, i32* %i
  %t32 = icmp sle i32 %t31, 2
  br i1 %t32, label %for_body14, label %for_end15
for_body14:
  store i32 0, i32* %j
  br label %for_start16
for_start16:
  %t33 = load i32, i32* %j
  %t34 = icmp sle i32 %t33, 3
  br i1 %t34, label %for_body17, label %for_end18
for_body17:
  %t35 = load i32, i32* %sum
  %t36 = load i32, i32* %i
  %t37 = load i32, i32* %j
  %t38 = getelementptr inbounds [3 x [4 x i32]], [3 x [4 x i32]]* %matrix, i32 0, i32 %t36, i32 %t37
  %t39 = load i32, i32* %t38
  %t40 = add i32 %t35, %t39
  store i32 %t40, i32* %sum
  %t41 = add i32 %t33, 1
  store i32 %t41, i32* %j
  br label %for_start16
for_end18:
  %t42 = add i32 %t31, 1
  store i32 %t42, i32* %i
  br label %for_start13
for_end15:
  %t43 = getelementptr inbounds [22 x i8], [22 x i8]* @.str6, i32 0, i32 0
  %t44 = getelementptr inbounds [3 x i8], [3 x i8]* @.str2, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t44, i8* %t43)
  %t45 = load i32, i32* %sum
  %t46 = getelementptr inbounds [3 x i8], [3 x i8]* @.str4, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t46, i32 %t45)
  %t47 = getelementptr inbounds [2 x i8], [2 x i8]* @.str3, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t47)
  ret i32 0
}

@.str1 = private constant [17 x i8] c"Matrix contents:\00"
@.str2 = private constant [3 x i8] c"%s\00"
@.str3 = private constant [2 x i8] c"\0A\00"
@.str4 = private constant [3 x i8] c"%d\00"
@.str5 = private constant [2 x i8] c" \00"
@.str6 = private constant [22 x i8] c"Sum of all elements: \00"