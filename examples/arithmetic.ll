; ModuleID = "oberon_module"
declare i32 @printf(i8*, ...)

define i32 @main() {
entry:
  %a = alloca i32
  %b = alloca i32
  %sum = alloca i32
  %product = alloca i32
  %x = alloca double
  %y = alloca double
  %result = alloca double
  store i32 10, i32* %a
  store i32 20, i32* %b
  %t1 = load i32, i32* %a
  %t2 = load i32, i32* %b
  %t3 = add i32 %t1, %t2
  store i32 %t3, i32* %sum
  %t4 = load i32, i32* %a
  %t5 = load i32, i32* %b
  %t6 = mul i32 %t4, %t5
  store i32 %t6, i32* %product
  store double 3.14, double* %x
  store double 2.0, double* %y
  %t7 = load double, double* %x
  %t8 = load double, double* %y
  %t9 = fmul double %t7, %t8
  store double %t9, double* %result
  %t10 = getelementptr inbounds [6 x i8], [6 x i8]* @.str1, i32 0, i32 0
  %t11 = getelementptr inbounds [3 x i8], [3 x i8]* @.str2, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t11, i8* %t10)
  %t12 = load i32, i32* %sum
  %t13 = getelementptr inbounds [3 x i8], [3 x i8]* @.str3, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t13, i32 %t12)
  %t14 = getelementptr inbounds [2 x i8], [2 x i8]* @.str4, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t14)
  %t15 = getelementptr inbounds [10 x i8], [10 x i8]* @.str5, i32 0, i32 0
  %t16 = getelementptr inbounds [3 x i8], [3 x i8]* @.str2, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t16, i8* %t15)
  %t17 = load i32, i32* %product
  %t18 = getelementptr inbounds [3 x i8], [3 x i8]* @.str3, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t18, i32 %t17)
  %t19 = getelementptr inbounds [2 x i8], [2 x i8]* @.str4, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t19)
  %t20 = getelementptr inbounds [14 x i8], [14 x i8]* @.str6, i32 0, i32 0
  %t21 = getelementptr inbounds [3 x i8], [3 x i8]* @.str2, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t21, i8* %t20)
  %t22 = load double, double* %result
  %t23 = getelementptr inbounds [3 x i8], [3 x i8]* @.str7, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t23, double %t22)
  %t24 = getelementptr inbounds [2 x i8], [2 x i8]* @.str4, i32 0, i32 0
  call i32 (i8*, ...) @printf(i8* %t24)
  ret i32 0
}

@.str1 = private constant [6 x i8] c"Sum: \00"
@.str2 = private constant [3 x i8] c"%s\00"
@.str3 = private constant [3 x i8] c"%d\00"
@.str4 = private constant [2 x i8] c"\0A\00"
@.str5 = private constant [10 x i8] c"Product: \00"
@.str6 = private constant [14 x i8] c"Real result: \00"
@.str7 = private constant [3 x i8] c"%f\00"