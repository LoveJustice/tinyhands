from rest_framework import serializers

from dataentry.models import Address1, Address2, InterceptionRecord, VictimInterview, BorderStation, Interceptee, Person


class Address1Serializer(serializers.ModelSerializer):
    class Meta:
        model = Address1


class CanonicalNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address2
        fields = ['id', 'name']


class Address2Serializer(serializers.ModelSerializer):
    class Meta:
        model = Address2
        depth = 1

    def create(self, validated_data):
        found_address1 = Address1.objects.get(pk=self.context['request'].data['address1']['id'])
        found_address2 = None
        if self.context['request'].data['canonical_name']['id'] == -1:
            found_address2 = None
        else:
            found_address2 = Address2.objects.get(pk=self.context['request'].data['canonical_name']['id'])
        validated_data['address1'] = found_address1
        validated_data['canonical_name'] = found_address2
        return Address2.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.address1 = Address1.objects.get(pk=self.context['request'].data['address1']['id'])
        instance.name = validated_data.get('name', instance.name)
        if self.context['request'].data['canonical_name']['id'] == -1:
            instance.canonical_name = None
        else:
            instance.canonical_name = Address2.objects.get(pk=self.context['request'].data['canonical_name']['id'])
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        instance.level = validated_data.get('level', instance.level)
	instance.verified = validated_data.get('verified', instance.verified)
        instance.save()
        return instance

    canonical_name = CanonicalNameSerializer()
    address1 = Address1Serializer()


class BorderStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorderStation


class InterceptionRecordListSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterceptionRecord
        fields = [
            'view_url',
            'edit_url',
            'delete_url',
            'id',
            'irf_number',
            'staff_name',
            'number_of_victims',
            'number_of_traffickers',
            'date_time_of_interception',
            'date_time_entered_into_system',
            'date_time_last_updated'
        ]

    view_url = serializers.HyperlinkedIdentityField(
        view_name='interceptionrecord_detail',
        read_only=True
    )
    edit_url = serializers.HyperlinkedIdentityField(
        view_name='interceptionrecord_update',
        read_only=True
    )
    delete_url = serializers.HyperlinkedIdentityField(
        view_name='InterceptionRecordDetail',
        read_only=True
    )


class InterceptionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterceptionRecord

    def validate(self, data):
        validation_response = {}
        errors = self.check_for_errors(data)
        warnings = self.check_for_warnings(data)
        if len(errors) > 0:
            validation_response['errors'] = errors
        if len(warnings) > 0:
            validation_response['warnings'] = warnings
        if len(warnings) > 0 or len(errors) > 0:
            raise serializers.ValidationError(validation_response)
        return data

    def check_for_errors(self, data): # For Error validation
        errors = []
        errors += self.check_for_none_checked(data)
        if data['contact_noticed'] == False and data['staff_noticed'] == False:
            errors.append({'contact_noticed': 'Either Contact (6.0) or Staff (7.0) must be chosen for how interception was made.'})
        return errors

    def check_for_none_checked(self, data): # For Error validation
        errors = []
        has_none_checked = True
        for field in data:
            if isinstance(data[field], bool) and data[field] == True:
                has_none_checked = False
        if has_none_checked:
            errors.append({'no_checkboxes_checked': 'At least one box must be checked on the first page.'})
        return errors

    def check_for_red_flags(self, data): # For Warning validation
        warnings = []
        any_red_flags = False
        for field in InterceptionRecord._meta.fields:
            try:
                if field.weight != None:
                    if data[field.name] == True:
                        any_red_flags = True
            except:
                pass
        if any_red_flags == False:
            warnings.append({'red_flags': 'No red flags are checked.'})
        return warnings

    def check_for_warnings(self, data): # For Warning validation
        warnings = []
        warnings += self.check_for_red_flags(data)
        warnings += self.check_procedure(data)
        warnings += self.check_type(data)
        if data['has_signature'] == False:
            warnings.append({'has_signature': 'Form should be signed, though not required.'})
        return warnings


    def check_procedure(self, data): # For Warning validation
        warnings = []
        if data['call_thn_to_cross_check'] == False:
            warnings.append({'call_thn_to_cross_check': 'Procedure not followed.'})
        if data['call_subcommittee_chair'] == False:
            warnings.append({'call_subcommittee_chair': 'Procedure not followed.'})
        if data['scan_and_submit_same_day'] == False:
            warnings.append({'scan_and_submit_same_day': 'Procedure not followed.'})
        return warnings

    def check_type(self, data): # For Warning validation
        warnings = []
        type_is_set = False
        for field in InterceptionRecord._meta.fields:
            try:
                if field.name:
                    if 'type' in field.name and data[field.name] == True:
                        type_is_set = True
            except:
                pass
        if type_is_set == False:
            warnings.append({'interception_type': 'Field should be included, though not required.'})
        return warnings




class VictimInterviewListSerializer(serializers.ModelSerializer):
    class Meta:
        model = VictimInterview
        fields = [
            'view_url',
            'edit_url',
            'delete_url',
            'id',
            'vif_number',
            'interviewer',
            'number_of_victims',
            'number_of_traffickers',
            'date',
            'date_time_entered_into_system',
            'date_time_last_updated'
        ]

    view_url = serializers.HyperlinkedIdentityField(
        view_name='victiminterview_detail',
        read_only=True
    )
    edit_url = serializers.HyperlinkedIdentityField(
        view_name='victiminterview_update',
        read_only=True
    )
    delete_url = serializers.HyperlinkedIdentityField(
        view_name='VictimInterviewDetail',
        read_only=True
    )


class VictimInterviewPersonBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = VictimInterview
        exclude = []


class VictimInterviewLocationBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = VictimInterview
        exclude = []


class VictimInterviewSerializer(serializers.ModelSerializer):
    victim_address1 = Address1Serializer(read_only=True)
    victim_address2 = Address2Serializer(read_only=True)
    victim_guardian_address1 = Address1Serializer(read_only=True)
    victim_guardian_address2 = Address2Serializer(read_only=True)

    class Meta:
        model = VictimInterview
        read_only_fields = ('person_boxes','location_boxes')
        fields = [
            'id',
            'vif_number',
            'interviewer',
            'number_of_victims',
            'number_of_traffickers',
            'date',
            'date_time_entered_into_system',
            'date_time_last_updated',
            'victim_gender',
            'location',
            'interviewer',
            'statement_read_before_beginning',
            'permission_to_use_photograph',
            'victim_name',
            'victim_address1',
            'victim_address2',
            'victim_address_ward',
            'victim_phone',
            'victim_age',
            'victim_height',
            'victim_weight',
            'person_boxes',
            'location_boxes',
            'victim_caste_magar',
            'victim_caste_jaisi',
            'victim_caste_thakuri',
            'victim_caste_brahmin',
            'victim_caste_chhetri',
            'victim_caste_newar',
            'victim_caste_tamang',
            'victim_caste_mongolian',
            'victim_caste_muslim',
            'victim_caste_madeshi_terai',
            'victim_caste_dalit',
            'victim_caste_dalit',
            'victim_caste_other_value',
            'victim_occupation_unemployed',
            'victim_occupation_farmer',
            'victim_occupation_wage_laborer',
            'victim_occupation_business_owner',
            'victim_occupation_migrant_worker',
            'victim_occupation_tailoring',
            'victim_occupation_housewife',
            'victim_occupation_animal_husbandry',
            'victim_occupation_domestic_work',
            'victim_occupation_shopkeeper',
            'victim_occupation_hotel',
            'victim_occupation_factory',
            'victim_occupation_other',
            'victim_occupation_other_value',
            'victim_marital_status_single',
            'victim_marital_status_widow',
            'victim_marital_status_divorced',
            'victim_marital_status_husband_has_other_wives',
            'victim_marital_status_abandoned_by_husband',
            'victim_lives_with_own_parents',
            'victim_lives_with_husband',
            'victim_lives_with_husbands_family',
            'victim_lives_with_friends',
            'victim_lives_with_alone',
            'victim_lives_with_other_relative',
            'victim_lives_with_other',
            'victim_lives_with_other_value',
            'victim_num_in_family',
            'victim_primary_guardian_own_parents',
            'victim_primary_guardian_husband',
            'victim_primary_guardian_other_relative',
            'victim_primary_guardian_non_relative',
            'victim_primary_guardian_no_one',
            'victim_guardian_address1',
            'victim_guardian_address2',
            'victim_guardian_address_ward',
            'victim_guardian_phone',
            'victim_parents_marital_status_single',
            'victim_parents_marital_status_married',
            'victim_parents_marital_status_widow',
            'victim_parents_marital_status_father_has_other_wives',
            'victim_parents_marital_separated',
            'victim_parents_marital_divorced',
            'victim_education_level_none',
            'victim_education_level_informal',
            'victim_education_level_primary',
            'victim_education_level_grade_4_8',
            'victim_education_level_grade_9_10',
            'victim_education_level_slc',
            'victim_education_level_11_12',
            'victim_education_level_bachelors',
            'victim_education_level_masters',
            'victim_is_literate',
            'migration_plans_education',
            'migration_plans_travel_tour',
            'migration_plans_shopping',
            'migration_plans_eloping',
            'migration_plans_arranged_marriage',
            'migration_plans_meet_own_family',
            'migration_plans_visit_brokers_home',
            'migration_plans_medical_treatment',
            'migration_plans_job_broker_didnt_say',
            'migration_plans_job_baby_care',
            'migration_plans_job_factory',
            'migration_plans_job_hotel',
            'migration_plans_job_shop',
            'migration_plans_job_laborer',
            'migration_plans_job_brothel',
            'migration_plans_job_household',
            'migration_plans_job_other',
            'migration_plans_other',
            'migration_plans_job_other_value',
            'migration_plans_other_value',
            'primary_motivation_support_myself',
            'primary_motivation_support_family',
            'primary_motivation_personal_debt',
            'primary_motivation_family_debt',
            'primary_motivation_love_marriage',
            'primary_motivation_bad_home_marriage',
            'primary_motivation_get_education',
            'primary_motivation_tour_travel',
            'primary_motivation_didnt_know',
            'primary_motivation_other',
            'primary_motivation_other_value',
            'victim_where_going_region_india',
            'victim_where_going_region_gulf',
            'victim_where_going_india_delhi',
            'victim_where_going_india_mumbai',
            'victim_where_going_india_surat',
            'victim_where_going_india_rajastan',
            'victim_where_going_india_kolkata',
            'victim_where_going_india_pune',
            'victim_where_going_india_jaipur',
            'victim_where_going_india_bihar',
            'victim_where_going_india_didnt_know',
            'victim_where_going_india_other',
            'victim_where_going_india_other_value',
            'victim_where_going_gulf_lebanon',
            'victim_where_going_gulf_dubai',
            'victim_where_going_gulf_malaysia',
            'victim_where_going_gulf_oman',
            'victim_where_going_gulf_saudi_arabia',
            'victim_where_going_gulf_kuwait',
            'victim_where_going_gulf_qatar',
            'victim_where_going_gulf_didnt_know',
            'victim_where_going_gulf_other',
            'victim_where_going_gulf_other_value',
            'manpower_involved',
            'victim_recruited_in_village',
            'brokers_relation_to_victim_own_dad',
            'brokers_relation_to_victim_own_mom',
            'brokers_relation_to_victim_own_uncle',
            'brokers_relation_to_victim_own_aunt',
            'brokers_relation_to_victim_own_bro',
            'brokers_relation_to_victim_own_sister',
            'brokers_relation_to_victim_own_other_relative',
            'brokers_relation_to_victim_friend',
            'brokers_relation_to_victim_agent',
            'brokers_relation_to_victim_husband',
            'brokers_relation_to_victim_boyfriend',
            'brokers_relation_to_victim_neighbor',
            'brokers_relation_to_victim_recently_met',
            'brokers_relation_to_victim_contractor',
            'brokers_relation_to_victim_other',
            'brokers_relation_to_victim_other_value',
            'victim_married_to_broker_years',
            'victim_married_to_broker_months',
            'victim_how_met_broker_from_community',
            'victim_how_met_broker_at_work',
            'victim_how_met_broker_at_school',
            'victim_how_met_broker_job_advertisement',
            'victim_how_met_broker_he_approached_me',
            'victim_how_met_broker_through_friends',
            'victim_how_met_broker_through_family',
            'victim_how_met_broker_at_wedding',
            'victim_how_met_broker_in_a_vehicle',
            'victim_how_met_broker_in_a_hospital',
            'victim_how_met_broker_went_myself',
            'victim_how_met_broker_called_my_mobile',
            'victim_how_met_broker_other',
            'victim_how_met_broker_other_value',
            'victim_how_met_broker_mobile_explanation',
            'victim_how_long_known_broker_years',
            'victim_how_long_known_broker_months',
            'victim_how_expense_was_paid_paid_myself',
            'victim_how_expense_was_paid_broker_paid_all',
            'victim_how_expense_was_paid_gave_money_to_broker',
            'victim_how_expense_was_paid_broker_gave_loan',
            'victim_how_expense_was_paid_amount',
            'broker_works_in_job_location_no',
            'broker_works_in_job_location_yes',
            'broker_works_in_job_location_dont_know',
            'amount_victim_would_earn',
            'number_broker_made_similar_promises_to',
            'victim_first_time_crossing_border',
            'victim_primary_means_of_travel_tourist_bus',
            'victim_primary_means_of_travel_motorbike',
            'victim_primary_means_of_travel_private_car',
            'victim_primary_means_of_travel_local_bus',
            'victim_primary_means_of_travel_microbus',
            'victim_primary_means_of_travel_plane',
            'victim_primary_means_of_travel_other',
            'victim_primary_means_of_travel_other_value',
            'victim_stayed_somewhere_between',
            'victim_how_long_stayed_between_days',
            'victim_how_long_stayed_between_start_date',
            'victim_was_hidden',
            'victim_was_hidden_explanation',
            'victim_was_free_to_go_out',
            'victim_was_free_to_go_out_explanation',
            'how_many_others_in_situation',
            'others_in_situation_age_of_youngest',
            'passport_made_no_passport_made',
            'passport_made_real_passport_made',
            'passport_made_passport_included_false_name',
            'passport_made_passport_included_other_false_info',
            'passport_made_passport_was_fake',
            'victim_passport_with_broker',
            'abuse_happened_sexual_harassment',
            'abuse_happened_sexual_abuse',
            'abuse_happened_physical_abuse',
            'abuse_happened_threats',
            'abuse_happened_denied_proper_food',
            'abuse_happened_forced_to_take_drugs',
            'abuse_happened_by_whom',
            'abuse_happened_explanation',
            'victim_traveled_with_broker_companion_yes',
            'victim_traveled_with_broker_companion_no',
            'victim_traveled_with_broker_companion_broker_took_me_to_border',
            'companion_with_when_intercepted',
            'planning_to_meet_companion_later',
            'money_changed_hands_broker_companion_no',
            'money_changed_hands_broker_companion_dont_know',
            'money_changed_hands_broker_companion_broker_gave_money',
            'money_changed_hands_broker_companion_companion_gave_money',
            'meeting_at_border_yes',
            'meeting_at_border_no',
            'meeting_at_border_meeting_broker',
            'meeting_at_border_meeting_companion',
            'victim_knew_details_about_destination',
            'other_involved_person_in_india',
            'other_involved_husband_trafficker',
            'other_involved_someone_met_along_the_way',
            'other_involved_someone_involved_in_trafficking',
            'other_involved_place_involved_in_trafficking',
            'victim_has_worked_in_sex_industry',
            'victim_place_worked_involved_sending_girls_overseas',
            'awareness_before_interception_had_heard_not_how_bad',
            'awareness_before_interception_knew_how_bad_not_happening_to_her',
            'awareness_before_interception_never_heard',
            'attitude_towards_tiny_hands_thankful',
            'attitude_towards_tiny_hands_blames',
            'attitude_towards_tiny_hands_doesnt_know',
            'victim_heard_gospel_no',
            'victim_heard_gospel_heard_name_only',
            'victim_heard_gospel_heard_but_never_believed',
            'victim_heard_gospel_already_believer',
            'victim_beliefs_now_doesnt_believe',
            'victim_beliefs_now_believes_no_church',
            'victim_beliefs_now_believes_and_church',
            'tiny_hands_rating_border_staff',
            'tiny_hands_rating_shelter_staff',
            'tiny_hands_rating_trafficking_awareness',
            'tiny_hands_rating_shelter_accommodations',
            'how_can_we_serve_you_better',
            'guardian_knew_was_travelling_to_india',
            'family_pressured_victim',
            'family_will_try_sending_again',
            'victim_feels_safe_at_home',
            'victim_wants_to_go_home',
            'victim_home_had_sexual_abuse_never',
            'victim_home_had_sexual_abuse_rarely',
            'victim_home_had_sexual_abuse_frequently',
            'victim_home_had_physical_abuse_never',
            'victim_home_had_physical_abuse_rarely',
            'victim_home_had_physical_abuse_frequently',
            'victim_home_had_emotional_abuse_never',
            'victim_home_had_emotional_abuse_rarely',
            'victim_home_had_emotional_abuse_frequently',
            'victim_guardian_drinks_alcohol_never',
            'victim_guardian_drinks_alcohol_occasionally',
            'victim_guardian_drinks_alcohol_all_the_time',
            'victim_guardian_uses_drugs_never',
            'victim_guardian_uses_drugs_occasionally',
            'victim_guardian_uses_drugs_all_the_time',
            'victim_family_economic_situation_no_basic_needs',
            'victim_family_economic_situation_difficult_basic_needs',
            'victim_family_economic_situation_comfortable_basic_needs',
            'victim_family_economic_situation_wealthy',
            'victim_had_suicidal_thoughts',
            'reported_total_situational_alarms'
        ]
        depth = 1


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = [
            'full_name',
            'gender',
            'age',
            'address1',
            'address2',
            'phone_contact',
        ]


class IntercepteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interceptee
        fields = [
            'photo',
            'id',
            'interception_record',
            'kind',
            'relation_to',
            'person',
        ]
    person = PersonSerializer()
