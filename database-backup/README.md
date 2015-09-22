# IRF - Interception Record Form #

    InterceptionRecord (model)
        Interceptee (child model)
       	    district
    		vdc

# VIF - Victim Interview Form #

    VictimInterview (model)
	    victim_address_district
        victim_address_vdc
		victim_guardian_address_district
		victim_guardian_address_vdc

        VictimInterviewPersonBox (child model)
		    address_district
			address_vdc

        VictimInterviewLocationBox (child model)
		    district
			vdc
