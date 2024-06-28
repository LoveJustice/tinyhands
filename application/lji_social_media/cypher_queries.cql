MATCH (source_profile:SourceProfile) RETURN source_profile LIMIT 25

MATCH path = (source_profile1:SourceProfile) -[]-(source_profile2:SourceProfile) RETURN path LIMIT 25

MATCH (source_profile:SourceProfile) WHERE ID(source_profile) = 5419 RETURN source_profile LIMIT 25

MATCH (source_profile:SourceProfile) WHERE ID(source_profile) = 7100 RETURN source_profile LIMIT 25

MATCH path = (source_profile:SourceProfile)-[]-(valid_name:ValidName)-[]-(person1:Person) WHERE ID(source_profile) = 7100 RETURN source_profile LIMIT 25

MATCH path = (source_profile:SourceProfile)-[]-(valid_name:ValidName)-[]-(person1:Person) WHERE ID(source_profile) = 5419 RETURN source_profile LIMIT 25

MATCH path1 = (source_profile1:SourceProfile)-[]-(valid_name1:ValidName)-[]-(person1:Person)-[]-(irf:IRF)<-[:ON_IRF]-(person2:Person)-[:HAS_NAME]-(valid_name2:ValidName)
WHERE ID(source_profile1) IN [5419, 7100]
OPTIONAL MATCH (person1) -[:HAS_MASTER_PERSON_ID]- (master1:MasterPerson),
              (person2) -[:HAS_MASTER_PERSON_ID]- (master2:MasterPerson)
RETURN path1, master1, master2
LIMIT 100;

MATCH path1 = (valid_name0:ValidName)- [:HAS_PROFILE_NAME]-(profile0:Profile)-[:IS_FRIENDS_WITH]-(source_profile1:SourceProfile)-[]-(valid_name1:ValidName)-[]-(person1:Person)-[]-(irf:IRF)<-[:ON_IRF]-(person2:Person)-[:HAS_NAME]-(valid_name2:ValidName)
WHERE ID(source_profile1) IN [5419, 7100]
OPTIONAL MATCH (person1) -[:HAS_MASTER_PERSON_ID]- (master1:MasterPerson),
              (person2) -[:HAS_MASTER_PERSON_ID]- (master2:MasterPerson)
RETURN path1, master1, master2
LIMIT 100;

MATCH path1 = (valid_nameX:ValidName)-[:HAS_NAME]-(personX:Person)-[:ON_IRF]-(irf0:IRF)-[:ON_IRF]-(person0:Person)-[:HAS_NAME]-(valid_name0:ValidName)- [:HAS_PROFILE_NAME]-(profile0:Profile)-[:IS_FRIENDS_WITH]-(source_profile1:SourceProfile)-[]-(valid_name1:ValidName)-[]-(person1:Person)-[]-(irf:IRF)<-[:ON_IRF]-(person2:Person)-[:HAS_NAME]-(valid_name2:ValidName)
WHERE ID(source_profile1) IN [5419, 7100]
OPTIONAL MATCH (person1) -[:HAS_MASTER_PERSON_ID]- (master1:MasterPerson),
              (person2) -[:HAS_MASTER_PERSON_ID]- (master2:MasterPerson),
              (personX) -[:HAS_MASTER_PERSON_ID]- (masterX:MasterPerson),
            (person0) -[:HAS_MASTER_PERSON_ID]- (master0:MasterPerson)
OPTIONAL MATCH (valid_name2) -[]- (profile2:Profile),
              (valid_nameX) -[]- (profileX:Profile)
OPTIONAL MATCH (roleX:Role) -[]- (personX)
OPTIONAL MATCH (role0:Role) -[]- (person0)
OPTIONAL MATCH (role1:Role) -[]- (person1)
OPTIONAL MATCH (role2:Role) -[]- (person2)
RETURN valid_nameX.full_name AS full_nameX
, personX.person_id AS person_idX
, irf0.irf_number AS irf_number0
, person0.person_id AS person_id0
, profile0.name AS friend
, ID(profile0) AS profile0_id
, source_profile1.name AS source_profile1_name
, ID(source_profile1) AS source_profile1_id
, valid_name1.full_name AS valid_name1_full_name
, person1.person_id AS person_id1
, irf.irf_number AS irf_number
, person2.person_id AS person_id2
, valid_name2.full_name AS full_name2
, master0.master_person_id AS master_person_id0
, master1.master_person_id AS master_person_id1
, master2.master_person_id AS master_person_id2
, masterX.master_person_id AS master_person_idX
, profileX.name AS profileX_name
, profile2.name AS profile2_name
, roleX.role AS roleX
, role0.role AS role0
, role1.role AS role1
, role2.role AS role2
LIMIT 100;

MATCH path1 = (valid_nameX:ValidName)-[:HAS_NAME]-(personX:Person)-[:ON_IRF]-(irf0:IRF)-[:ON_IRF]-(person0:Person)-[:HAS_NAME]-(valid_name0:ValidName)-[:HAS_PROFILE_NAME]-(profile0:Profile)-[:IS_FRIENDS_WITH]-(source_profile1:SourceProfile)-[]-(valid_name1:ValidName)-[]-(person1:Person)-[]-(irf:IRF)<-[:ON_IRF]-(person2:Person)-[:HAS_NAME]-(valid_name2:ValidName)
WHERE ID(source_profile1) IN [5419, 7100]

OPTIONAL MATCH path2 = (person1) -[:HAS_MASTER_PERSON_ID]- (master1:MasterPerson),
              (person2) -[:HAS_MASTER_PERSON_ID]- (master2:MasterPerson),
              (personX) -[:HAS_MASTER_PERSON_ID]- (masterX:MasterPerson),
              (person0) -[:HAS_MASTER_PERSON_ID]- (master0:MasterPerson)

OPTIONAL MATCH (valid_name2) -[]- (profile2:Profile),
              (valid_nameX) -[]- (profileX:Profile)

OPTIONAL MATCH (roleX:Role) -[]- (personX),
              (role0:Role) -[]- (person0),
              (role1:Role) -[]- (person1),
              (role2:Role) -[]- (person2)

RETURN path1, path2,
       valid_nameX, personX, irf0, person0, valid_name0, profile0, source_profile1, valid_name1, person1, irf, person2, valid_name2,
       master1, master2, masterX, master0,
       profile2, profileX,
       roleX, role0, role1, role2
LIMIT 100;

RETURN valid_nameX.full_name AS full_nameX
, personX.person_id AS person_idX
, irf0.irf_number AS irf_number0
, person0.person_id AS person_id0
, profile0.name AS friend
, ID(profile0) AS profile0_id
, source_profile1.name AS source_profile1_name
, ID(source_profile1) AS source_profile1_id
, valid_name1.full_name AS valid_name1_full_name
, person1.person_id AS person_id1
, irf.irf_number AS irf_number
, person2.person_id AS person_id2
, valid_name2.full_name AS full_name2
, master0.master_person_id AS master_person_id0
, master1.master_person_id AS master_person_id1
, master2.master_person_id AS master_person_id2
, masterX.master_person_id AS master_person_idX
, profileX.name AS profileX_name
, profile2.name AS profile2_name
, roleX.role AS roleX
, role0.role AS role0
, role1.role AS role1
, role2.role AS role2
LIMIT 100;

MATCH path1 = (valid_nameX:ValidName)-[:HAS_NAME]-(personX:Person)-[:ON_IRF]-(irf0:IRF)-[:ON_IRF]-(person0:Person)-[:HAS_NAME]-(valid_name0:ValidName)-[:HAS_PROFILE_NAME]-(profile0:Profile)-[:IS_FRIENDS_WITH]-(source_profile1:SourceProfile)-[]-(valid_name1:ValidName)-[]-(person1:Person)-[]-(irf:IRF)<-[:ON_IRF]-(person2:Person)-[:HAS_NAME]-(valid_name2:ValidName)
WHERE ID(source_profile1) IN [5419, 7100]

OPTIONAL MATCH path2 = (person1) -[:HAS_MASTER_PERSON_ID]- (master1:MasterPerson),
              (person2) -[:HAS_MASTER_PERSON_ID]- (master2:MasterPerson),
              (personX) -[:HAS_MASTER_PERSON_ID]- (masterX:MasterPerson),
              (person0) -[:HAS_MASTER_PERSON_ID]- (master0:MasterPerson)

OPTIONAL MATCH path3 = (valid_name2) -[]- (profile2:Profile),
              (valid_nameX) -[]- (profileX:Profile)

OPTIONAL MATCH path4 = (roleX:Role) -[]- (personX),
              (role0:Role) -[]- (person0),
              (role1:Role) -[]- (person1),
              (role2:Role) -[]- (person2)

RETURN path1, path2, path2, path4

LIMIT 100;


MATCH path1 = (source_profile1:SourceProfile)-[]-(valid_name1:ValidName)-[]-(person1:Person)-[]-(irf:IRF)<-[:ON_IRF]-(person2:Person)-[:HAS_NAME]-(valid_name2:ValidName)
WHERE ID(source_profile1) IN [5419, 7100]
OPTIONAL MATCH (person1) -[:HAS_MASTER_PERSON_ID]- (master1:MasterPerson),
              (person2) -[:HAS_MASTER_PERSON_ID]- (master2:MasterPerson)
RETURN source_profile1.name AS source_profile1_name
, valid_name1.full_name AS valid_name1_full_name
, person1.person_id AS person_id1
, irf.irf_number AS irf_number
, person2.person_id AS person_id2
, valid_name2.full_name AS full_name2
, master1.master_person_id AS master_person_id1
, master2.master_person_id AS master_person_id2
LIMIT 100;

MATCH (profile:Profile) WHERE profile.url='https://www.facebook.com' RETURN profile LIMIT 10;

MATCH (profile:Profile)
WHERE profile.url =~ '(?i).*errol.*'
RETURN profile LIMIT 10;

MATCH (profile:Profile)
WHERE profile.name =~ '(?i).*matimba.*'
RETURN profile LIMIT 10;

MATCH (profile:Profile)
WHERE profile.url =~ '(?i).*friends.*'
RETURN profile LIMIT 10;

MATCH (profile:Profile)
WHERE profile.url =~ '(?i).*web.*'
RETURN profile LIMIT 10;

MATCH (profile:Profile)
WHERE profile.url =~ '(?i).*muw.*'
RETURN COUNT(profile);

MATCH (profile1:Profile) (profile2:Profile)
WHERE profile1.name = profile2.name
RETURN COUNT(profile1);

MATCH path = (source_profile1:SourceProfile)-[]-()-[]-(source_profile2:SourceProfile) WHERE ID(source_profile1) IN [6708]
RETURN path LIMIT 10;

MATCH (profile:Profile)
WHERE profile.url =~ '(?i).*web.*'
DETACH DELETE profile

MATCH (profile1:Profile),(profile2:Profile)
WHERE profile1.url = profile2.url AND ID(profile1)<>ID(profile2) AND ID(profile1)<ID(profile2)
RETURN profile1, profile2 LIMIT 4


MATCH (profile:Profile) WHERE profile.name = 'Chotika Pannak' RETURN profile LIMIT 10;
│(:Profile:SourceProfile {name: "Chotika Pannak",url: "https://www.face│
│book.com"})
│(:Profile:SourceProfile {existing: true,name: "Sombut Phothong",url: "│
│https://www.facebook.com"})                                           │

│(:Profile:SourceProfile {existing: true,new: true,name: "Chezntembavip│
│ Walvisbay",url: "https://www.facebook.com"})


https://www.facebook.com/profile.php?id=100093481306971

MATCH (profile:Profile) WHERE profile.url = 'https://web.facebook.com/juanthaiwok' OR profile.url = 'https://web.facebook.com/juanthaiwok' OR profile.url = 'https://facebook.com/juanthaiwok';
RETURN profile;

MATCH (source_profile1:SourceProfile)
RETURN source_profile1.name AS name, source_profile1.url as url
ORDER BY name DESC;

MATCH (sp:Profile)-[r]-()
WITH sp.name AS name, sp.url AS url, COUNT(r) AS numberOfConnections
ORDER BY numberOfConnections DESC
RETURN name, url, numberOfConnections
LIMIT 50;

MATCH (name:Name)-[r]-()
WITH name.name AS name, COUNT(r) AS numberOfConnections
ORDER BY numberOfConnections DESC
RETURN name, numberOfConnections
LIMIT 50;

MATCH path = (startProfile:Profile {id: 466423})-[*]->(person:Person)
WHERE ALL(node in nodes(path) WHERE node:Profile OR node:Person)
RETURN person, [node in nodes(path) WHERE node:Profile] AS profileNodesAlongPath

MATCH path = (startProfile:Profile)-[*]-(valid_name:ValidName)
             WHERE NONE(node in nodes(path) WHERE node:Role OR node:WorkText AND (node:Name AND NOT node:ValidName)) AND ID(startProfile) IN [466423,466098,626]
             RETURN valid_name.name as name, [node in nodes(path) WHERE node:Profile] AS profileNodesAlongPath LIMIT 10;

MATCH path = (startProfile:Profile)-[*]-(valid_name:ValidName)
WHERE
    ANY(node in nodes(path) WHERE node:Person) AND
    ANY(node in nodes(path) WHERE node:IRF) AND
    NONE(node in nodes(path) WHERE node:Role OR node:WorkText OR (node:Name AND NOT node:ValidName))
    AND ID(startProfile) IN [466423,466098,626]
RETURN valid_name.name as name, [node in nodes(path) WHERE node:Profile] AS profileNodesAlongPath
LIMIT 10;


MATCH path = (startProfile:Profile)-[*..6]-(valid_name:ValidName)
WHERE
    ANY(node in nodes(path) WHERE node:Person) AND
    ANY(node in nodes(path) WHERE node:IRF) AND
    NONE(node in nodes(path) WHERE node:Role OR node:WorkText OR (node:Name AND NOT node:ValidName))
    AND ID(startProfile) IN [466423,466098,626]
RETURN path
LIMIT 20;


MATCH path = (startProfile:Profile)-[*..4]-(validname:ValidName)-[]-(person1:Person)-[]-(irf:IRF)
WHERE
    ANY(node in nodes(path) WHERE node:Person) AND
    ANY(node in nodes(path) WHERE node:IRF) AND
    NONE(node in nodes(path) WHERE node:Role OR node:WorkText OR (node:Name AND NOT node:ValidName))
    AND ID(startProfile) IN [466423,466098,626]
RETURN path
LIMIT 20;

MATCH path = (startProfile:Profile)-[*..4]-(validname:ValidName)-[]-(person1:Person)-[]-(irf:IRF)
WHERE
    ANY(node in nodes(path) WHERE node:Person) AND
    ANY(node in nodes(path) WHERE node:IRF) AND
    NONE(node in nodes(path) WHERE node:Role OR node:WorkText OR (node:Name AND NOT node:ValidName))
    AND ID(startProfile) IN [6708]
RETURN path
LIMIT 100;

MATCH path = (startProfile:Profile)-[*..4]-(validname:ValidName)-[]-(person1:Person)-[]-(irf:IRF)
WHERE
    ANY(node in nodes(path) WHERE node:Person) AND
    ANY(node in nodes(path) WHERE node:IRF) AND
    NONE(node in nodes(path) WHERE node:Role OR node:WorkText OR (node:Name AND NOT node:ValidName))
    AND ID(startProfile) IN [466423,466098,626]
RETURN path
LIMIT 100;


Assistant, I want to turn the following cypher query into a report good enough to base a police case on:

MATCH path = (startProfile:Profile)-[*..4]-(validname:ValidName)-[]-(person1:Person)-[]-(irf:IRF)
WHERE
    ID(startProfile) IN [466423] AND
    ANY(node in nodes(path) WHERE node:Person) AND
    ANY(node in nodes(path) WHERE node:IRF) AND
    NONE(node in nodes(path) WHERE node:Role OR node:WorkText OR (node:Name AND NOT node:ValidName))
    AND size(nodes(path)) = size(apoc.coll.toSet(nodes(path)))
OPTIONAL MATCH (person1)-[:HAS_NAME]->(name:Name)
OPTIONAL MATCH (person1)-[:HAS_ROLE]->(role:Role)
OPTIONAL MATCH (person1)-[:HAS_MASTER_PERSON_ID]->(master_person:MasterPerson)
WITH irf.irf_number AS irf_number, person1.person_id AS person_id,
     [node in nodes(path) WHERE node:Profile | node.name] AS profile_names,
     [node in nodes(path) WHERE node:Profile | node.url] AS profile_urls,
     name.full_name AS full_name,
     role.role AS role,
     master_person.master_person_id AS master_person_id
CALL apoc.cypher.doIt(
  "MATCH (n:Name {full_name: $full_name})-[:HAS_NAME]-(p:Person)-[:HAS_MASTER_PERSON_ID]->(mp:MasterPerson) RETURN COUNT(DISTINCT mp.master_person_id) AS count",
  {full_name: full_name}
) YIELD value
RETURN irf_number, person_id, profile_names, profile_urls, full_name, role, master_person_id, value.count AS unique_master_person_id_count
LIMIT 1000;


I want to generate a report that will assist police in pursuing one or more suspects using the results of the following cypher query and a graph database:
```
MATCH path = (startProfile:Profile)-[*..3]-(validname:ValidName)-[]-(person1:Person)-[]-(irf:IRF)
WHERE
    ID(startProfile) IN [466737] AND
    ANY(node in nodes(path) WHERE node:Person) AND
    ANY(node in nodes(path) WHERE node:IRF) AND
    NONE(node in nodes(path) WHERE node:Role OR node:WorkText OR (node:Name AND NOT node:ValidName))
    AND size(nodes(path)) = size(apoc.coll.toSet(nodes(path)))
OPTIONAL MATCH (person1)-[:HAS_NAME]->(name:Name)
OPTIONAL MATCH (person1)-[:HAS_ROLE]->(role:Role)
OPTIONAL MATCH (person1)-[:HAS_MASTER_PERSON_ID]->(master_person:MasterPerson)
WITH irf.irf_number AS irf_number, person1.person_id AS person_id,
     [node in nodes(path) WHERE node:Profile | node.name] AS profile_names,
     [node in nodes(path) WHERE node:Profile | node.url] AS profile_urls,
     name.full_name AS full_name,
     role.role AS role,
     master_person.master_person_id AS master_person_id
CALL apoc.cypher.doIt(
  "MATCH (n:Name {full_name: $full_name})-[:HAS_NAME]-(p:Person)-[:HAS_MASTER_PERSON_ID]->(mp:MasterPerson) RETURN COUNT(DISTINCT mp.master_person_id) AS count",
  {full_name: full_name}
) YIELD value
RETURN irf_number, person_id, size(profile_names) AS degree, profile_names, profile_urls, full_name, role, master_person_id, value.count AS unique_master_person_id_count
LIMIT 1000;
```
As you can see, here are two data sources or networks in my graph database. The one is a database of persons (with person_id property), Name (name property) and IRF nodes.  An IRF node can be thought of as an incident or an intercept.    One or more Persons may belong to an IRF node.  Persons have a Name node which may have the ValidName label.  The second network is that of social media profiles (SMPs).  A single SMP is connected to the Person graph through the ValidName node.  Which means we have found the SMP of a Person via a name. An SMP is thought to be of degree 1 if it is the SMP of a person of on an IRF.  SMP are connected to other SMPs via a IS_FRIENDS_WITH or FOLLOWS relationship.  A friend of a degree 1 SMP is a degree 2 SMP.  The cypher query above takes one or more SMPs (via their IDs) and attempts to connect it to the Person graph via the ValidName label (which may be up to n degrees away and ultimately an IRF node and all the Person nodes attached to that IRF.  The report should highlight the SourceProfile, the intermediate profiles (as a list if necessary) the Validname connection into the Persons graph, then person_id and finally the IRF to which the Person belongs.  A person also has a Role (role property) node via the HAS_ROLE relationship from the Person node.  Essential columns for the report are:
startProfile.name, startProfile.url, [Profile.urls],  validname.name, Person.person_id, Role.role, irf.irf_number.





config.DATABASE_URL = "bolt://username:password@localhost:7687"

MATCH (name:Name)-[r]-(person:Person)-[s]-(master_person:MasterPerson)
WHERE name.name = 'Chotika Pannak'
RETURN COUNT(s) AS count, master_person.master_person_id AS master_person_id, person.person_id AS person_id, name.name AS name;

The followimg query
MATCH path = (startProfile:Profile)-[*..4]-(validname:ValidName)-[]-(person1:Person)-[]-(irf:IRF)
WHERE
    ID(startProfile) IN [466423] AND
    ANY(node in nodes(path) WHERE node:Person) AND
    ANY(node in nodes(path) WHERE node:IRF) AND
    NONE(node in nodes(path) WHERE node:Role OR node:WorkText OR (node:Name AND NOT node:ValidName))
    AND size(nodes(path)) = size(apoc.coll.toSet(nodes(path)))
OPTIONAL MATCH (person1)-[:HAS_NAME]->(name:Name)
OPTIONAL MATCH (person1)-[:HAS_ROLE]->(role:Role)
OPTIONAL MATCH (person1)-[:HAS_MASTER_PERSON_ID]->(master_person:MasterPerson)
WITH irf.irf_number AS irf_number, person1.person_id AS person_id,
     [node in nodes(path) WHERE node:Profile | node.name] AS profile_names,
     [node in nodes(path) WHERE node:Profile | node.url] AS profile_urls,
     name.full_name AS full_name,
     role.role AS role,
     master_person.master_person_id AS master_person_id
CALL apoc.cypher.doIt(
  "MATCH (n:Name {full_name: $full_name})-[:HAS_NAME]-(p:Person)-[:HAS_MASTER_PERSON_ID]->(mp:MasterPerson) RETURN COUNT(DISTINCT mp.master_person_id) AS count",
  {full_name: full_name}
) YIELD value
RETURN irf_number, person_id, profile_names, profile_urls, full_name, role, master_person_id, value.count AS unique_master_person_id_count
LIMIT 1000;


Profile confirmation script:
MATCH path1 = (irf:IRF)-[:ON_IRF]-(person1:Person)-[:HAS_NAME]-(valid_name1:ValidName)-[:HAS_PROFILE_NAME]-(profile1:Profile)-[IS_FRIENDS_WITH]-(profile:Profile),
MATCH path2 = (irf:IRF)-[]-(person2:Person)-[:HAS_NAME]-(valid_name2:ValidName)-[:HAS_PROFILE_NAME]-(profile2:Profile)-[IS_FRIENDS_WITH]-(profile:Profile)
RETURN path1, path2

MATCH path1 = (irf:IRF)-[:ON_IRF]-(person1:Person)-[:HAS_NAME]-(valid_name1:ValidName)-[:HAS_PROFILE_NAME]-(profile1:Profile)-[r1:IS_FRIENDS_WITH]-(profile:Profile),
      path2 = (irf)-[:ON_IRF]-(person2:Person)-[:HAS_NAME]-(valid_name2:ValidName)-[:HAS_PROFILE_NAME]-(profile2:Profile)-[r2:IS_FRIENDS_WITH]-(profile)
WHERE person1 <> person2
RETURN path1, path2;

suspect = [466423, 466098, 626]

We are given one name Willem Heinrich Pretorius. This name is associated to two Social Media profiles:
'url: https:willemheinrich.pretorius.7' ID[466423] and 'url: https:heinie.pretorius' ID[466098].  Let"'"s call them WHP and HP respectively.
These two individuals are friends via their SMPs.   WHP is directly associated with two IRF numbers, JNB014 and JNB047 (degree 1 association).  There are 6 other individuals associated with these IRFs.
Both WHP and HP are friends with CafeThai Benoni ('url: http:/juan.vanniekerk.77') [<id>: 466165] and Rukchnok van Niekerk ('url: https:/rukchnok.vanniekerk.9') [<id>: 471060].  CafeThai Benoni and Rukchnok van Niekerk are friends via their SMPs. CafeThai Benoni is also connected with a profile 'url: /juanthaiwok' and name Juan Van Niekerk which seems the same person or owner of the CafeThai Benoni.

Both share friendship with Candice Geyer Da Cunha ('url: https://www.facebook.com/candice.cunha.14') [<id>: 626].


The following IRFs are connected to some any degree between 1 and 3 with the persons of this network:
['APP095', 'APP291', 'APP530', 'APP570', 'APP635', 'APP654',
       'APP905', 'BER046', 'BGN211', 'BRT327', 'BWS152', 'CML011',
       'CML191', 'CML222', 'COT162', 'CTA046', 'DAC1175', 'DAR272',
       'DAR332', 'FTN232', 'GAR038', 'GLR265', 'JGN017', 'JNB014',
       'JNB027', 'JNB046', 'JNB047', 'JNB105', 'JNB129', 'JNB196',
       'JNB222', 'LIM100', 'LLG022', 'MNZ036', 'MPT320', 'MRL012',
       'MRL035', 'NBI039', 'NDL052', 'NDL1089', 'NDL1475', 'NDL1497',
       'NDL1554', 'NDL1747', 'NDL1961', 'NDL2079', 'NDL2413', 'NDL260',
       'NDL466', 'NDL478', 'NDL671', 'NPJ744', 'OSK105', 'PRS160']

The social media profile names that occur the most often in this network Willem Heinrich Pretorius,Heinie Pretorius, Tammy Wong, Riccardo Pretoruis.
The new name is that of Tammy Wong ('url: https://www.facebook.com/profile.php?id=100093668737649') or [<id>: 466737].  She is friends with all the individual mentioned above.




MATCH path = (profile:Profile)-[]-()-(person:Person)-[]-(irf:IRF) WHERE ID(profile) = 466423 RETURN path LIMIT 10;

MATCH path = (tammy:Profile)-[]-(profile:Profile) WHERE ID(tammy) = 466737 AND ID(profile) IN [466423, 466098, 626,] RETURN path LIMIT 10;

 Here are screenshots of networks I have shown before in our meetings.  They are of the database and there are also raw images of  networks only.  Let me know if this works for you, or if there are more detail you want to see.

The images are a selection of networks for profiles of persons NOT in SearchLight but who are connected to individuals who are.  Two of these individuals are Tammy Wong and Errol Tjipuka.  They sit more or less cental to the networks.  Tammy Wongs network reveal other interconnected profiles that may inturn be connected to Search light individuals. Pink nodes are social media profiles.  Blue are Searchlight persons.  Brown are IRFs.  Grey nodes are for names, social media sub headings or trafficking roles.

MATCH path = (startProfile:Profile)-[*..3]-(validname:ValidName)-[]-(person1:Person)-[]-(irf:IRF)
WHERE
    ID(startProfile) IN [466423, 466098, 626, 466737] AND
    ANY(node in nodes(path) WHERE node:Person) AND
    ANY(node in nodes(path) WHERE node:IRF) AND
    NONE(node in nodes(path) WHERE node:Role OR node:WorkText OR (node:Name AND NOT node:ValidName))
    AND size(nodes(path)) = size(apoc.coll.toSet(nodes(path)))
OPTIONAL MATCH (person1)-[:HAS_NAME]->(name:Name)
OPTIONAL MATCH (person1)-[:HAS_ROLE]->(role:Role)
OPTIONAL MATCH (person1)-[:HAS_PHOTO]->(photo:Photo)
OPTIONAL MATCH (person1)-[:HAS_MASTER_PERSON_ID]->(master_person:MasterPerson)
CALL apoc.cypher.doIt(
  "MATCH (n:Name {full_name: $full_name})-[:HAS_NAME]-(p:Person)-[:HAS_MASTER_PERSON_ID]->(mp:MasterPerson) RETURN COUNT(DISTINCT mp.master_person_id) AS count",
  {full_name: name.full_name}
) YIELD value
WHERE value.count<=10
RETURN path
LIMIT 1000;


MATCH path = (startProfile:Profile)-[*..3]-(validname:ValidName)-[]-(person1:Person)-[]-(irf:IRF)
WHERE
    ID(startProfile) IN [6708] AND
    ANY(node in nodes(path) WHERE node:Person) AND
    ANY(node in nodes(path) WHERE node:IRF) AND
    NONE(node in nodes(path) WHERE node:Role OR node:WorkText OR (node:Name AND NOT node:ValidName))
    AND size(nodes(path)) = size(apoc.coll.toSet(nodes(path)))
OPTIONAL MATCH (person1)-[:HAS_NAME]->(name:Name)
OPTIONAL MATCH (person1)-[:HAS_ROLE]->(role:Role)
OPTIONAL MATCH (person1)-[:HAS_PHOTO]->(photo:Photo)
OPTIONAL MATCH (person1)-[:HAS_MASTER_PERSON_ID]->(master_person:MasterPerson)
CALL apoc.cypher.doIt(
  "MATCH (n:Name {full_name: $full_name})-[:HAS_NAME]-(p:Person)-[:HAS_MASTER_PERSON_ID]->(mp:MasterPerson) RETURN COUNT(DISTINCT mp.master_person_id) AS count",
  {full_name: name.full_name}
) YIELD value
WHERE value.count<=10
RETURN path
LIMIT 1000;


MATCH path = (startProfile:Profile)-[*..3]-(validname:ValidName)-[]-(person1:Person)-[]-(irf:IRF)
WHERE
    ID(startProfile) IN [6708, 6285, 464161, 465333] AND
    ANY(node in nodes(path) WHERE node:Person) AND
    ANY(node in nodes(path) WHERE node:IRF) AND
    NONE(node in nodes(path) WHERE node:Role OR node:WorkText OR (node:Name AND NOT node:ValidName))
    AND size(nodes(path)) = size(apoc.coll.toSet(nodes(path)))
WITH path, person1, irf
UNWIND [node in nodes(path) WHERE node:Person] AS personNode
OPTIONAL MATCH (personNode)-[:HAS_NAME]->(name:Name)-[]-(valid_name:ValidName)-[:HAS_PROFILE_NAME]-(profile1:Profile)
OPTIONAL MATCH (personNode)-[:HAS_ROLE]->(role:Role)
OPTIONAL MATCH (personNode)-[:HAS_PHOTO]->(photo:Photo)
OPTIONAL MATCH (irf)-[:AT_BORDER_STATION]->(border_station:BorderStation)-[:IN_COUNTRY]->(country:Country)
OPTIONAL MATCH (irf)<-[:ON_IRF]-(:Person)-[:HAS_PHOTO]->(:Photo)
OPTIONAL MATCH (personNode)-[:HAS_MASTER_PERSON_ID]->(master_person:MasterPerson)
OPTIONAL MATCH (irf)<-[:ON_IRF]-(person:Person)
CALL apoc.cypher.doIt(
  "MATCH (n:Name {full_name: $full_name})-[:HAS_NAME]-(p:Person)-[:HAS_MASTER_PERSON_ID]->(mp:MasterPerson) RETURN COUNT(DISTINCT mp.master_person_id) AS count",
  {full_name: COALESCE(name.full_name, '')}
) YIELD value
WHERE value.count<=10
WITH personNode, person1, irf, name, border_station, country
RETURN personNode.person_id as person_id
, person1.person_id as profile_person
, COALESCE(name.full_name, 'No Name') as full_name
, irf.irf_number AS irf_number
, COALESCE(country.country, 'Unknown Country') AS country
, COALESCE(border_station.border_station, 'Unknown Border Station') AS border_station
, profile1.url AS profile1_url
LIMIT 1000;

[node in nodes(path) WHERE node:Profile | node.name] AS profile_names,

MATCH path = (startProfile:Profile)-[*..3]-(validname:ValidName)-[]-(person1:Person)-[]-(irf:IRF)
WHERE
    ID(startProfile) IN [466423, 466098, 626, 466737] AND
    ANY(node in nodes(path) WHERE node:Person) AND
    ANY(node in nodes(path) WHERE node:IRF) AND
    NONE(node in nodes(path) WHERE node:Role OR node:WorkText OR (node:Name AND NOT node:ValidName))
    AND size(nodes(path)) = size(apoc.coll.toSet(nodes(path)))
WITH startProfile, path, person1, irf, [node in nodes(path) WHERE node:Profile | node.name] AS profile_names, [node in nodes(path) WHERE node:Profile | node.url] AS profile_urls
UNWIND [node in nodes(path) WHERE node:Person] AS personNode
OPTIONAL MATCH (personNode)-[:HAS_NAME]->(person_name:Name)-[:HAS_PROFILE_NAME]-(profile1:Profile)
OPTIONAL MATCH (personNode)-[:HAS_ROLE]->(role:Role)
OPTIONAL MATCH (personNode)-[:HAS_PHOTO]->(photo:Photo)
OPTIONAL MATCH (irf)-[:AT_BORDER_STATION]->(border_station:BorderStation)
OPTIONAL MATCH (border_station)-[:IN_COUNTRY]->(country:Country)
OPTIONAL MATCH (irf)<-[:ON_IRF]-(person:Person)
OPTIONAL MATCH (person)-[:HAS_MASTER_PERSON_ID]->(master_person:MasterPerson)
OPTIONAL MATCH (person)-[:HAS_NAME]-(other_person_name:Name)
RETURN
startProfile.name AS start_profile
,country.name AS country
,border_station.name AS border_station
,irf.irf_number AS irf_number
,person.person_id AS person_id
,other_person_name.name AS searchlight_person_name
,person_name.name AS person1_name
,profile1.url AS profile1_url
,profile_names
,profile_urls
, size(profile_names) AS degree_of_separation

LIMIT 5000;

MATCH path = (startProfile:Profile)-[*..3]-(validname:ValidName)-[]-(person1:Person)-[]-(irf:IRF)
WHERE
    ID(startProfile) IN [6708, 6285, 464161, 465333] AND
    ANY(node in nodes(path) WHERE node:Person) AND
    ANY(node in nodes(path) WHERE node:IRF) AND
    NONE(node in nodes(path) WHERE node:Role OR node:WorkText OR (node:Name AND NOT node:ValidName))
    AND size(nodes(path)) = size(apoc.coll.toSet(nodes(path)))
WITH startProfile, ID(startProfile) AS start_profile_id, path, person1, irf, [node in nodes(path) WHERE node:Profile | node.name] AS profile_names, [node in nodes(path) WHERE node:Profile | node.url] AS profile_urls
UNWIND [node in nodes(path) WHERE node:Person] AS personNode
OPTIONAL MATCH (personNode)-[:HAS_NAME]->(person_name:Name)-[:HAS_PROFILE_NAME]-(profile1:Profile)
OPTIONAL MATCH (personNode)-[:HAS_ROLE]->(role:Role)
OPTIONAL MATCH (personNode)-[:HAS_PHOTO]->(photo:Photo)
OPTIONAL MATCH (irf)-[:AT_BORDER_STATION]->(border_station:BorderStation)
OPTIONAL MATCH (border_station)-[:IN_COUNTRY]->(country:Country)
OPTIONAL MATCH (irf)<-[:ON_IRF]-(person:Person)
OPTIONAL MATCH (person)-[:HAS_NAME]-(other_person_name:Name)
OPTIONAL MATCH (person)-[:HAS_MASTER_PERSON_ID]->(master_person:MasterPerson)
CALL apoc.cypher.doIt(
  "MATCH (n:Name {name: $person_name})-[:HAS_NAME]-(p:Person)-[:HAS_MASTER_PERSON_ID]->(mp:MasterPerson) RETURN COUNT(DISTINCT mp.master_person_id) AS count",
  {person_name: person_name.name}
) YIELD value
WHERE value.count <=10
WITH path, startProfile, country, border_station, irf, person, other_person_name, person_name, master_person, profile1
RETURN
    ,path
    ,startProfile
    ,country
    ,border_station
    ,irf
    ,other_person_name
    ,master_person
    ,person_name
    ,profile1

LIMIT 5;

MATCH path = (name:Name)-[]-(profile_other:Profile)-[]-(profile:Profile)-[r]-(valid_name:ValidName)
WHERE ID(profile) = 565152
RETURN path LIMIT 10;
