!-------------------------------------------------------------------------!
!                                                                         !
!        N  A  S     P A R A L L E L     B E N C H M A R K S  3.4         !
!                                                                         !
!                       O p e n M P     V E R S I O N                     !
!                                                                         !
!                                   L U                                   !
!                                                                         !
!-------------------------------------------------------------------------!
!                                                                         !
!    This benchmark is an OpenMP version of the NPB LU code.              !
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
! Authors: S. Weeratunga
!          V. Venkatakrishnan
!          E. Barszcz
!          M. Yarrow
!          H. Jin
!
!---------------------------------------------------------------------

!---------------------------------------------------------------------
      program applu
!---------------------------------------------------------------------

!---------------------------------------------------------------------
!
!   driver for the performance evaluation of the solver for
!   five coupled parabolic/elliptic partial differential equations.
!
!---------------------------------------------------------------------

      use lu_data
      implicit none

      character class
      logical verified

      integer i

      

!---------------------------------------------------------------------
!     Setup info for timers
!---------------------------------------------------------------------


!---------------------------------------------------------------------
!   read input data
!---------------------------------------------------------------------
      call read_input()

!---------------------------------------------------------------------
!   set up domain sizes
!---------------------------------------------------------------------
      call domain()

      call alloc_space

!---------------------------------------------------------------------
!   set up coefficients
!---------------------------------------------------------------------
      call setcoeff()

!---------------------------------------------------------------------
!   set the boundary values for dependent variables
!---------------------------------------------------------------------
      call setbv()

!---------------------------------------------------------------------
!   set the initial values for dependent variables
!---------------------------------------------------------------------
      call setiv()

!---------------------------------------------------------------------
!   compute the forcing term based on prescribed exact solution
!---------------------------------------------------------------------
      call erhs()

!---------------------------------------------------------------------
!   perform one SSOR iteration to touch all data pages
!---------------------------------------------------------------------
      call ssor(1)

!---------------------------------------------------------------------
!   reset the boundary and initial values
!---------------------------------------------------------------------
      call setbv()
      call setiv()

!---------------------------------------------------------------------
!   perform the SSOR iterations
!---------------------------------------------------------------------
      call roi_begin
      call ssor(itmax)
      call roi_end
!---------------------------------------------------------------------
!   compute the solution error
!---------------------------------------------------------------------
      call error()

!---------------------------------------------------------------------
!   compute the surface integral
!---------------------------------------------------------------------
      call pintgr()

!---------------------------------------------------------------------
!   verification test
!---------------------------------------------------------------------
      call verify ( rsdnm, errnm, frc, class, verified )

      call print_results('LU', class, nx0,  &
     &  ny0, nz0, itmax,  &
     &   '          floating point', verified,  &
     &  npbversion, compiletime, cs1, cs2, cs3, cs4, cs5, cs6,  &
     &  '(none)')

!---------------------------------------------------------------------
!      More timers
!---------------------------------------------------------------------

 999  continue
      end


