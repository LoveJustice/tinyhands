from rest_framework import serializers

from dataentry.models import Address1, Address2, InterceptionRecord, VictimInterview, BorderStation


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

class VictimInterviewSerializer(serializers.ModelSerializer):
        class Meta:
            model = VictimInterview
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
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                'abuse_happened_physical_abuse',
                'abuse_happened_denied_proper_food',
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
                'meeting_at_border_meeting_broker',
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
