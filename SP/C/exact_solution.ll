; ModuleID = 'FIRModule'
source_filename = "FIRModule"
target datalayout = "e-m:e-i8:8:32-i16:16:32-i64:64-i128:128-n32:64-S128"
target triple = "aarch64-unknown-linux-gnu"

%struct.ident_t = type { i32, i32, i32, i32, ptr }

@_QMsp_dataEbuf = external global [5 x [162 x double]]
@_QMsp_dataEce = external local_unnamed_addr global [13 x [5 x double]]
@_QMsp_dataEcuf = external global [162 x double]
@_QMsp_dataEq = external global [162 x double]
@_QMsp_dataEue = external global [5 x [162 x double]]
@0 = private unnamed_addr constant [23 x i8] c";unknown;unknown;0;0;;\00", align 1
@1 = private unnamed_addr constant %struct.ident_t { i32 0, i32 2, i32 0, i32 22, ptr @0 }, align 8
@_QMsp_dataEbuf.cache = common global ptr null, align 8
@_QMsp_dataEcuf.cache = common global ptr null, align 8
@_QMsp_dataEq.cache = common global ptr null, align 8
@_QMsp_dataEue.cache = common global ptr null, align 8

; Function Attrs: nounwind
define void @exact_solution_(ptr nocapture readonly %0, ptr nocapture readonly %1, ptr nocapture readonly %2, ptr nocapture writeonly %3) local_unnamed_addr #0 {
  %omp_global_thread_num3 = tail call i32 @__kmpc_global_thread_num(ptr nonnull @1)
  %5 = tail call ptr @__kmpc_threadprivate_cached(ptr nonnull @1, i32 %omp_global_thread_num3, ptr nonnull @_QMsp_dataEbuf, i64 6480, ptr nonnull @_QMsp_dataEbuf.cache)
  %6 = tail call ptr @__kmpc_threadprivate_cached(ptr nonnull @1, i32 %omp_global_thread_num3, ptr nonnull @_QMsp_dataEcuf, i64 1296, ptr nonnull @_QMsp_dataEcuf.cache)
  %7 = tail call ptr @__kmpc_threadprivate_cached(ptr nonnull @1, i32 %omp_global_thread_num3, ptr nonnull @_QMsp_dataEq, i64 1296, ptr nonnull @_QMsp_dataEq.cache)
  %8 = tail call ptr @__kmpc_threadprivate_cached(ptr nonnull @1, i32 %omp_global_thread_num3, ptr nonnull @_QMsp_dataEue, i64 6480, ptr nonnull @_QMsp_dataEue.cache)
  %9 = load double, ptr %0, align 8, !tbaa !4
  %10 = load double, ptr %1, align 8, !tbaa !10
  %11 = load double, ptr %2, align 8, !tbaa !12
  %12 = load double, ptr @_QMsp_dataEce, align 8, !tbaa !14
  %13 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 1, i64 0), align 8, !tbaa !14
  %14 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 4, i64 0), align 8, !tbaa !14
  %15 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 7, i64 0), align 8, !tbaa !14
  %16 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 10, i64 0), align 8, !tbaa !14
  %17 = fmul contract double %9, %16
  %18 = fadd contract double %15, %17
  %19 = fmul contract double %9, %18
  %20 = fadd contract double %14, %19
  %21 = fmul contract double %9, %20
  %22 = fadd contract double %13, %21
  %23 = fmul contract double %9, %22
  %24 = fadd contract double %12, %23
  %25 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 2, i64 0), align 8, !tbaa !14
  %26 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 5, i64 0), align 8, !tbaa !14
  %27 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 8, i64 0), align 8, !tbaa !14
  %28 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 11, i64 0), align 8, !tbaa !14
  %29 = fmul contract double %10, %28
  %30 = fadd contract double %27, %29
  %31 = fmul contract double %10, %30
  %32 = fadd contract double %26, %31
  %33 = fmul contract double %10, %32
  %34 = fadd contract double %25, %33
  %35 = fmul contract double %10, %34
  %36 = fadd contract double %24, %35
  %37 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 3, i64 0), align 8, !tbaa !14
  %38 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 6, i64 0), align 8, !tbaa !14
  %39 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 9, i64 0), align 8, !tbaa !14
  %40 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 12, i64 0), align 8, !tbaa !14
  %41 = fmul contract double %11, %40
  %42 = fadd contract double %39, %41
  %43 = fmul contract double %11, %42
  %44 = fadd contract double %38, %43
  %45 = fmul contract double %11, %44
  %46 = fadd contract double %37, %45
  %47 = fmul contract double %11, %46
  %48 = fadd contract double %36, %47
  store double %48, ptr %3, align 8, !tbaa !17
  %49 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 0, i64 1), align 8, !tbaa !14
  %50 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 1, i64 1), align 8, !tbaa !14
  %51 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 4, i64 1), align 8, !tbaa !14
  %52 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 7, i64 1), align 8, !tbaa !14
  %53 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 10, i64 1), align 8, !tbaa !14
  %54 = fmul contract double %9, %53
  %55 = fadd contract double %52, %54
  %56 = fmul contract double %9, %55
  %57 = fadd contract double %51, %56
  %58 = fmul contract double %9, %57
  %59 = fadd contract double %50, %58
  %60 = fmul contract double %9, %59
  %61 = fadd contract double %49, %60
  %62 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 2, i64 1), align 8, !tbaa !14
  %63 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 5, i64 1), align 8, !tbaa !14
  %64 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 8, i64 1), align 8, !tbaa !14
  %65 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 11, i64 1), align 8, !tbaa !14
  %66 = fmul contract double %10, %65
  %67 = fadd contract double %64, %66
  %68 = fmul contract double %10, %67
  %69 = fadd contract double %63, %68
  %70 = fmul contract double %10, %69
  %71 = fadd contract double %62, %70
  %72 = fmul contract double %10, %71
  %73 = fadd contract double %61, %72
  %74 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 3, i64 1), align 8, !tbaa !14
  %75 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 6, i64 1), align 8, !tbaa !14
  %76 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 9, i64 1), align 8, !tbaa !14
  %77 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 12, i64 1), align 8, !tbaa !14
  %78 = fmul contract double %11, %77
  %79 = fadd contract double %76, %78
  %80 = fmul contract double %11, %79
  %81 = fadd contract double %75, %80
  %82 = fmul contract double %11, %81
  %83 = fadd contract double %74, %82
  %84 = fmul contract double %11, %83
  %85 = fadd contract double %73, %84
  %86 = getelementptr i8, ptr %3, i64 8
  store double %85, ptr %86, align 8, !tbaa !17
  %87 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 0, i64 2), align 8, !tbaa !14
  %88 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 1, i64 2), align 8, !tbaa !14
  %89 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 4, i64 2), align 8, !tbaa !14
  %90 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 7, i64 2), align 8, !tbaa !14
  %91 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 10, i64 2), align 8, !tbaa !14
  %92 = fmul contract double %9, %91
  %93 = fadd contract double %90, %92
  %94 = fmul contract double %9, %93
  %95 = fadd contract double %89, %94
  %96 = fmul contract double %9, %95
  %97 = fadd contract double %88, %96
  %98 = fmul contract double %9, %97
  %99 = fadd contract double %87, %98
  %100 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 2, i64 2), align 8, !tbaa !14
  %101 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 5, i64 2), align 8, !tbaa !14
  %102 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 8, i64 2), align 8, !tbaa !14
  %103 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 11, i64 2), align 8, !tbaa !14
  %104 = fmul contract double %10, %103
  %105 = fadd contract double %102, %104
  %106 = fmul contract double %10, %105
  %107 = fadd contract double %101, %106
  %108 = fmul contract double %10, %107
  %109 = fadd contract double %100, %108
  %110 = fmul contract double %10, %109
  %111 = fadd contract double %99, %110
  %112 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 3, i64 2), align 8, !tbaa !14
  %113 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 6, i64 2), align 8, !tbaa !14
  %114 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 9, i64 2), align 8, !tbaa !14
  %115 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 12, i64 2), align 8, !tbaa !14
  %116 = fmul contract double %11, %115
  %117 = fadd contract double %114, %116
  %118 = fmul contract double %11, %117
  %119 = fadd contract double %113, %118
  %120 = fmul contract double %11, %119
  %121 = fadd contract double %112, %120
  %122 = fmul contract double %11, %121
  %123 = fadd contract double %111, %122
  %124 = getelementptr i8, ptr %3, i64 16
  store double %123, ptr %124, align 8, !tbaa !17
  %125 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 0, i64 3), align 8, !tbaa !14
  %126 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 1, i64 3), align 8, !tbaa !14
  %127 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 4, i64 3), align 8, !tbaa !14
  %128 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 7, i64 3), align 8, !tbaa !14
  %129 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 10, i64 3), align 8, !tbaa !14
  %130 = fmul contract double %9, %129
  %131 = fadd contract double %128, %130
  %132 = fmul contract double %9, %131
  %133 = fadd contract double %127, %132
  %134 = fmul contract double %9, %133
  %135 = fadd contract double %126, %134
  %136 = fmul contract double %9, %135
  %137 = fadd contract double %125, %136
  %138 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 2, i64 3), align 8, !tbaa !14
  %139 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 5, i64 3), align 8, !tbaa !14
  %140 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 8, i64 3), align 8, !tbaa !14
  %141 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 11, i64 3), align 8, !tbaa !14
  %142 = fmul contract double %10, %141
  %143 = fadd contract double %140, %142
  %144 = fmul contract double %10, %143
  %145 = fadd contract double %139, %144
  %146 = fmul contract double %10, %145
  %147 = fadd contract double %138, %146
  %148 = fmul contract double %10, %147
  %149 = fadd contract double %137, %148
  %150 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 3, i64 3), align 8, !tbaa !14
  %151 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 6, i64 3), align 8, !tbaa !14
  %152 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 9, i64 3), align 8, !tbaa !14
  %153 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 12, i64 3), align 8, !tbaa !14
  %154 = fmul contract double %11, %153
  %155 = fadd contract double %152, %154
  %156 = fmul contract double %11, %155
  %157 = fadd contract double %151, %156
  %158 = fmul contract double %11, %157
  %159 = fadd contract double %150, %158
  %160 = fmul contract double %11, %159
  %161 = fadd contract double %149, %160
  %162 = getelementptr i8, ptr %3, i64 24
  store double %161, ptr %162, align 8, !tbaa !17
  %163 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 0, i64 4), align 8, !tbaa !14
  %164 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 1, i64 4), align 8, !tbaa !14
  %165 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 4, i64 4), align 8, !tbaa !14
  %166 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 7, i64 4), align 8, !tbaa !14
  %167 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 10, i64 4), align 8, !tbaa !14
  %168 = fmul contract double %9, %167
  %169 = fadd contract double %166, %168
  %170 = fmul contract double %9, %169
  %171 = fadd contract double %165, %170
  %172 = fmul contract double %9, %171
  %173 = fadd contract double %164, %172
  %174 = fmul contract double %9, %173
  %175 = fadd contract double %163, %174
  %176 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 2, i64 4), align 8, !tbaa !14
  %177 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 5, i64 4), align 8, !tbaa !14
  %178 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 8, i64 4), align 8, !tbaa !14
  %179 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 11, i64 4), align 8, !tbaa !14
  %180 = fmul contract double %10, %179
  %181 = fadd contract double %178, %180
  %182 = fmul contract double %10, %181
  %183 = fadd contract double %177, %182
  %184 = fmul contract double %10, %183
  %185 = fadd contract double %176, %184
  %186 = fmul contract double %10, %185
  %187 = fadd contract double %175, %186
  %188 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 3, i64 4), align 8, !tbaa !14
  %189 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 6, i64 4), align 8, !tbaa !14
  %190 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 9, i64 4), align 8, !tbaa !14
  %191 = load double, ptr getelementptr inbounds ([13 x [5 x double]], ptr @_QMsp_dataEce, i64 0, i64 12, i64 4), align 8, !tbaa !14
  %192 = fmul contract double %11, %191
  %193 = fadd contract double %190, %192
  %194 = fmul contract double %11, %193
  %195 = fadd contract double %189, %194
  %196 = fmul contract double %11, %195
  %197 = fadd contract double %188, %196
  %198 = fmul contract double %11, %197
  %199 = fadd contract double %187, %198
  %200 = getelementptr i8, ptr %3, i64 32
  store double %199, ptr %200, align 8, !tbaa !17
  ret void
}

; Function Attrs: nounwind
declare i32 @__kmpc_global_thread_num(ptr) local_unnamed_addr #1

; Function Attrs: nounwind
declare ptr @__kmpc_threadprivate_cached(ptr, i32, ptr, i64, ptr) local_unnamed_addr #1

attributes #0 = { nounwind "frame-pointer"="non-leaf" "target-cpu"="generic" "target-features"="+outline-atomics,+v8a,+fp-armv8,+neon" }
attributes #1 = { nounwind }

!llvm.module.flags = !{!0, !1, !2, !3}

!0 = !{i32 2, !"Debug Info Version", i32 3}
!1 = !{i32 7, !"openmp", i32 11}
!2 = !{i32 8, !"PIC Level", i32 2}
!3 = !{i32 7, !"PIE Level", i32 2}
!4 = !{!5, !5, i64 0}
!5 = !{!"dummy arg data/_QFexact_solutionExi", !6, i64 0}
!6 = !{!"dummy arg data", !7, i64 0}
!7 = !{!"any data access", !8, i64 0}
!8 = !{!"any access", !9, i64 0}
!9 = !{!"Flang function root _QPexact_solution"}
!10 = !{!11, !11, i64 0}
!11 = !{!"dummy arg data/_QFexact_solutionEeta", !6, i64 0}
!12 = !{!13, !13, i64 0}
!13 = !{!"dummy arg data/_QFexact_solutionEzeta", !6, i64 0}
!14 = !{!15, !15, i64 0}
!15 = !{!"global data/_QMsp_dataEce", !16, i64 0}
!16 = !{!"global data", !7, i64 0}
!17 = !{!18, !18, i64 0}
!18 = !{!"dummy arg data/_QFexact_solutionEdtemp", !6, i64 0}
