!-------------------------------------------------------------------------!
!                                                                         !
!        N  A  S     P A R A L L E L     B E N C H M A R K S  3.4         !
!                                                                         !
!                       O p e n M P     V E R S I O N                     !
!                                                                         !
!                                   S P                                   !
!                                                                         !
!-------------------------------------------------------------------------!
!                                                                         !
!    This benchmark is an OpenMP version of the NPB SP code.              !
!    It is described in NAS Technical Report 99-011.                      !
!                                                                         !
!    Permission to use, copy, distribute and modify this software         !
!    for any purpose with or without fee is hereby granted.  We           !
!    request, however, that all derived work reference the NAS            !
!    Parallel Benchmarks 3.4. This software is provided "as is"           !
!    without express or implied warranty.                                 !
!                                                                         !
!    Information on NPB 3.4, including the technical report, the          !
!    original specifications, source code, results and information        !
!    on how to submit new results, is available at:                       !
!                                                                         !
!           http://www.nas.nasa.gov/Software/NPB/                         !
!                                                                         !
!    Send comments or suggestions to  npb@nas.nasa.gov                    !
!                                                                         !
!          NAS Parallel Benchmarks Group                                  !
!          NASA Ames Research Center                                      !
!          Mail Stop: T27A-1                                              !
!          Moffett Field, CA   94035-1000                                 !
!                                                                         !
!          E-mail:  npb@nas.nasa.gov                                      !
!          Fax:     (650) 604-3957                                        !
!                                                                         !
!-------------------------------------------------------------------------!

!---------------------------------------------------------------------
!
! Authors: R. Van der Wijngaart
!          W. Saphir
!          H. Jin
!---------------------------------------------------------------------

!---------------------------------------------------------------------
       program SP
!---------------------------------------------------------------------

       use sp_data
       implicit none

       include 'blk_par.h'

       integer          i, niter, step, fstatus
       double precision  n3
       logical          verified
       character        class
!$     integer  omp_get_max_threads
!$     external omp_get_max_threads

      

!---------------------------------------------------------------------
!      Read input file (if it exists), else take
!      defaults from parameters
!---------------------------------------------------------------------

       write(*, 1000)
       open (unit=2,file='inputsp.data',status='old', iostat=fstatus)

       if (fstatus .eq. 0) then
         write(*,233) 
 233     format(' Reading from input file inputsp.data')
         read (2,*) niter
         read (2,*) dt
         read (2,*) grid_points(1), grid_points(2), grid_points(3)
         close(2)
       else
         write(*,234) 
         niter = niter_default
         dt    = dt_default
         grid_points(1) = problem_size
         grid_points(2) = problem_size
         grid_points(3) = problem_size
       endif
 234   format(' No input file inputsp.data. Using compiled defaults')

       write(*, 1001) grid_points(1), grid_points(2), grid_points(3)
       write(*, 1002) niter, dt
       if (blkdim .gt. 0) write(*, 1004) blkdim
!$     write(*, 1003) omp_get_max_threads()
       write(*, *)

 1000  format(//, ' NAS Parallel Benchmarks (NPB3.4-OMP)',  &
     &            ' - SP Benchmark', /)
 1001  format(' Size: ', i4, 'x', i4, 'x', i4)
 1002  format(' Iterations: ', i4, '    dt:  ', f11.7)
 1003  format(' Number of available threads: ', i5)
 1004  format(' Dimension blocking size: ', i5)

       if ( (grid_points(1) .gt. IMAX) .or.  &
     &      (grid_points(2) .gt. JMAX) .or.  &
     &      (grid_points(3) .gt. KMAX) ) then
             print *, (grid_points(i),i=1,3)
             print *,' Problem size too big for compiled array sizes'
             goto 999
       endif
       nx2 = grid_points(1) - 2
       ny2 = grid_points(2) - 2
       nz2 = grid_points(3) - 2

       call alloc_space

       call set_constants

       call exact_rhs

       call initialize

!---------------------------------------------------------------------
!      do one time step to touch all code, and reinitialize
!---------------------------------------------------------------------
       call adi
       call initialize

       call roi_begin

       do  step = 1, niter

          if (mod(step, 20) .eq. 0 .or. step .eq. 1) then
             write(*, 200) step
 200         format(' Time step ', i4)
          endif

          call adi

       end do
       
       call roi_end
       
       call verify(niter, class, verified)

      call print_results('SP', class, grid_points(1),  &
     &     grid_points(2), grid_points(3), niter,  &
     &      '          floating point',  &
     &     verified, npbversion,compiletime, cs1, cs2, cs3, cs4, cs5,  &
     &     cs6, '(none)')

!---------------------------------------------------------------------
!      More timers
!---------------------------------------------------------------------

 999   continue

       end
