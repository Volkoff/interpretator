; ModuleID = "oberon_module"
declare i32 @printf(i8*, ...)

define i32 @main() {
entry:
  %i = alloca i32
  %r = alloca double
  %s = alloca i8*
  %arr = alloca i32, align 8
  store i32 42, i32* %i
  store double 3.14, double* %r
  %t1 = getelementptr inbounds [6 x i8], [6 x i8]* @.str1, i32 0, i32 0
  store i8* %t1, i8** %s
  %t2 = load i32, i32* %i
  %t3 = getelementptr inbounds i32, i32* %arr, i32 0
  store i32 %t2, i32* %t3
  %t4 = getelementptr inbounds i32, i32* %arr, i32 1
  store i32 10, i32* %t4
  %t5 = getelementptr inbounds [9 x i8], [9 x i8]* @.str2, i32 0, i32 0
  %t6 = getelementptr inbounds [3 x i8], [3 x i8]* @.str3, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t6, i8* %t5)
  %t7 = load i32, i32* %i
  %t8 = getelementptr inbounds [3 x i8], [3 x i8]* @.str4, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t8, i32 %t7)
  %t9 = getelementptr inbounds [2 x i8], [2 x i8]* @.str5, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t9)
  %t10 = getelementptr inbounds [6 x i8], [6 x i8]* @.str6, i32 0, i32 0
  %t11 = getelementptr inbounds [3 x i8], [3 x i8]* @.str3, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t11, i8* %t10)
  %t12 = load double, double* %r
  %t13 = getelementptr inbounds [3 x i8], [3 x i8]* @.str7, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t13, double %t12)
  %t14 = getelementptr inbounds [2 x i8], [2 x i8]* @.str5, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t14)
  %t15 = getelementptr inbounds [8 x i8], [8 x i8]* @.str8, i32 0, i32 0
  %t16 = getelementptr inbounds [3 x i8], [3 x i8]* @.str3, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t16, i8* %t15)
  %t17 = load i8*, i8** %s
  %t18 = getelementptr inbounds [3 x i8], [3 x i8]* @.str3, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t18, i8* %t17)
  %t19 = getelementptr inbounds [2 x i8], [2 x i8]* @.str5, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t19)
  %t20 = getelementptr inbounds [10 x i8], [10 x i8]* @.str9, i32 0, i32 0
  %t21 = getelementptr inbounds [3 x i8], [3 x i8]* @.str3, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t21, i8* %t20)
  %t22 = getelementptr inbounds i32, i32* %arr, i32 0
  %t23 = load i32, i32* %t22
  %t24 = getelementptr inbounds [3 x i8], [3 x i8]* @.str4, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t24, i32 %t23)
  %t25 = getelementptr inbounds [2 x i8], [2 x i8]* @.str5, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t25)
  %t26 = getelementptr inbounds [10 x i8], [10 x i8]* @.str10, i32 0, i32 0
  %t27 = getelementptr inbounds [3 x i8], [3 x i8]* @.str3, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t27, i8* %t26)
  %t28 = getelementptr inbounds i32, i32* %arr, i32 1
  %t29 = load i32, i32* %t28
  %t30 = getelementptr inbounds [3 x i8], [3 x i8]* @.str4, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t30, i32 %t29)
  %t31 = getelementptr inbounds [2 x i8], [2 x i8]* @.str5, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t31)
  ret i32 0
}

@.str1 = private constant [6 x i8] c"Hello\00"
@.str2 = private constant [9 x i8] c"Integer:\00"
@.str3 = private constant [3 x i8] c"%s\00"
@.str4 = private constant [3 x i8] c"%d\00"
@.str5 = private constant [2 x i8] c"\0A\00"
@.str6 = private constant [6 x i8] c"Real:\00"
@.str7 = private constant [3 x i8] c"%f\00"
@.str8 = private constant [8 x i8] c"String:\00"
@.str9 = private constant [10 x i8] c"Array[0]:\00"
@.str10 = private constant [10 x i8] c"Array[1]:\00"