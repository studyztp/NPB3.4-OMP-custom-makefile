! CLASS = E
!  
!  
!  This file is generated automatically by the setparams utility.
!  It sets the number of processors and the class of the NPB
!  in this directory. Do not modify it by hand.
!  
        integer nx, ny, nz, maxdim, niter_default
        parameter (nx=4096, ny=2048, nz=2048, maxdim=4096)
        parameter (niter_default=25)
        integer kind2
        parameter (kind2=8)
        logical  convertdouble
        parameter (convertdouble = .false.)
        character compiletime*11
        parameter (compiletime='12 Sep 2024')
        character npbversion*5
        parameter (npbversion='3.4.2')
        character cs1*6
        parameter (cs1='(none)')
        character cs2*5
        parameter (cs2='$(FC)')
        character cs3*6
        parameter (cs3='(none)')
        character cs4*6
        parameter (cs4='(none)')
        character cs5*6
        parameter (cs5='(none)')
        character cs6*9
        parameter (cs6='$(FFLAGS)')
        character cs7*6
        parameter (cs7='randi8')
