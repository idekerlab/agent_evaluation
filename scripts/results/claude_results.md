## Paragraph 1

An intricate network regulates the activities of SIRT1 and PARP1 proteins and continues to be uncovered. Both SIRT1 and PARP1 share a common co-factor nicotinamide adenine dinucleotide (NAD+) and several common substrates, including regulators of DNA damage response and circadian rhythms. We review this complex network using an interactive Molecular Interaction Map (MIM) to explore the interplay between these two proteins. Here we discuss how NAD + competition and post-transcriptional/translational feedback mechanisms create a regulatory network sensitive to environmental cues, such as genotoxic stress and metabolic states, and examine the role of those interactions in DNA repair and ultimately, cell fate decisions.

HGNC:14929 = **SIRT1**     
MESH:D000071137 = **Poly (ADP-Ribose) Polymerase-1**     
HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
CHEBI:CHEBI:23357 = **cofactor**     
CHEBI:CHEBI:15846 = **NAD(+)**     
CHEBI:CHEBI:15846 = **NAD(+)**     
GO:GO:0006974 = **DNA damage response**     
GO:GO:0007623 = **circadian rhythm**     
MESH:D016454 = **Review**     
MESH:D019532 = **Map**     
HGNC:20443 = **MTSS1**     
CHEBI:CHEBI:13389 = **NAD**     
MESH:D005246 = **Feedback**     
MESH:D003463 = **Cues**     
GO:GO:0006281 = **DNA repair**     

*Both SIRT1 and PARP1 share a common co-factor nicotinamide adenine dinucleotide (NAD+)*
- `complex(p(HGNC:SIRT1), a(CHEBI:"NAD(+)")) hasComponent a(CHEBI:"NAD(+)")`

*Both SIRT1 and PARP1 share a common co-factor nicotinamide adenine dinucleotide (NAD+)*
- `complex(p(HGNC:PARP1), a(CHEBI:"NAD(+)")) hasComponent a(CHEBI:"NAD(+)")`

*Both SIRT1 and PARP1 share several common substrates, including regulators of DNA damage response*
- `p(HGNC:SIRT1) reg bp(GO:"DNA damage response")`

*Both SIRT1 and PARP1 share several common substrates, including regulators of DNA damage response*
- `p(HGNC:PARP1) reg bp(GO:"DNA damage response")`

*Both SIRT1 and PARP1 share several common substrates, including regulators of circadian rhythms*
- `p(HGNC:SIRT1) reg bp(GO:"circadian rhythm")`

*Both SIRT1 and PARP1 share several common substrates, including regulators of circadian rhythms*
- `p(HGNC:PARP1) reg bp(GO:"circadian rhythm")`

*NAD+ competition and post-transcriptional/translational feedback mechanisms create a regulatory network*
- `a(CHEBI:"NAD(+)") decreases act(p(HGNC:SIRT1))`

*NAD+ competition and post-transcriptional/translational feedback mechanisms create a regulatory network*
- `a(CHEBI:"NAD(+)") decreases act(p(HGNC:PARP1))`

*examine the role of those interactions in DNA repair and ultimately, cell fate decisions*
- `p(HGNC:SIRT1) reg bp(GO:"DNA repair")`

*examine the role of those interactions in DNA repair and ultimately, cell fate decisions*
- `p(HGNC:PARP1) reg bp(GO:"DNA repair")`



## Paragraph 2

SIRT1 and PARP1 are enzymes that affect two key post-translational modifications: acetylation and ADP-ribosylation, respectively, for a diverse group of proteins. These enzymes are functionally connected due to their use of a common substrate, nicotinamide adenine dinucleotide (NAD+) . Recent studies suggest that these proteins participate in common pathways providing cells with a mechanism for balancing cell survival and death. A well-developed understanding of activity overlap of these proteins may provide insights into the biology of these two proteins as they are actively being pursued as therapeutic targets in a range of conditions, including cancer and metabolic disorders .

HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
MESH:D004798 = **Enzymes**     
MESH:D000339 = **Affect**     
GO:GO:0043687 = **post-translational protein modification**     
MESH:D000107 = **Acetylation**     
MESH:D000074744 = **ADP-Ribosylation**     
MESH:D004798 = **Enzymes**     
EFO:0005061 = **substrate**     
CHEBI:CHEBI:15846 = **NAD(+)**     
CHEBI:CHEBI:15846 = **NAD(+)**     
MESH:D013534 = **Survival**     
GO:GO:0008219 = **cell death**     
MESH:D032882 = **Comprehension**     
MESH:D001695 = **Biology**     
MESH:D013812 = **Therapeutics**     
MESH:D009369 = **Neoplasms**     
MESH:D008659 = **Metabolic Diseases**     

*SIRT1 and PARP1 are enzymes that affect two key post-translational modifications: acetylation and ADP-ribosylation, respectively, for a diverse group of proteins.*
- `p(HGNC:SIRT1) hasActivity ma(MESH:Acetylation)`

*SIRT1 and PARP1 are enzymes that affect two key post-translational modifications: acetylation and ADP-ribosylation, respectively, for a diverse group of proteins.*
- `p(HGNC:PARP1) hasActivity ma(MESH:"ADP-Ribosylation")`

*These enzymes are functionally connected due to their use of a common substrate, nicotinamide adenine dinucleotide (NAD+).*
- `p(HGNC:SIRT1) regulates a(CHEBI:"NAD(+)")`

*These enzymes are functionally connected due to their use of a common substrate, nicotinamide adenine dinucleotide (NAD+).*
- `p(HGNC:PARP1) regulates a(CHEBI:"NAD(+)")`

*Recent studies suggest that these proteins participate in common pathways providing cells with a mechanism for balancing cell survival and death.*
- `composite(p(HGNC:SIRT1), p(HGNC:PARP1)) regulates bp(GO:"cell survival")`

*Recent studies suggest that these proteins participate in common pathways providing cells with a mechanism for balancing cell survival and death.*
- `composite(p(HGNC:SIRT1), p(HGNC:PARP1)) regulates bp(GO:"cell death")`



## Paragraph 3

In this review, we look at the role of each of these two proteins using a Molecular Interaction Map (MIM) that visually integrates the experimental findings of the regulatory pathways that surround these proteins, shown in Figure  1. The MIM helps free readers from a linear view of events and gain a better understanding of control loops involved in these pathways . A machine-readable version of the MIM is provided as Additional file 1 viewable using PathVisio-MIM ( http://discover.nci.nih.gov/mim/mim_pathvisio.html) . Additionally, the MIM covers in greater detail the interactions surrounding SIRT1 and PARP1; a complete list of annotations is also provided as Additional file 2.

MESH:D016454 = **Review**     
MESH:D019532 = **Map**     
HGNC:20443 = **MTSS1**     
HGNC:20443 = **MTSS1**     
MESH:D032882 = **Comprehension**     
HGNC:20443 = **MTSS1**     
HGNC:20443 = **MTSS1**     
HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     

*The MIM covers in greater detail the interactions surrounding SIRT1 and PARP1*
- `complex(p(HGNC:SIRT1), p(HGNC:PARP1)) reg bp(GO:"cellular process")`



## Paragraph 4

SIRT1 and PARP1 Molecular Interaction Map. Blue: Post-translational modifications, Red: Inhibition and cleavage, Green: Stimulation and catalysis.

HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
MESH:D019532 = **Map**     
GO:GO:0043687 = **post-translational protein modification**     
MESH:D002384 = **Catalysis**     

*Blue: Post-translational modifications*
- `p(HGNC:SIRT1) reg p(HGNC:PARP1, pmod(Ub))`

*Red: Inhibition and cleavage*
- `p(HGNC:PARP1) directlyDecreases p(HGNC:SIRT1)`

*Green: Stimulation and catalysis*
- `p(HGNC:SIRT1) increases act(p(HGNC:PARP1))`



## Paragraph 5

Figure  2 shows a modular overview of how the SIRT1 and PARP1 interactions are laid out (an arrow indicates that a molecule or process from the source module has an interaction with a molecule or process in the target module) and Figure  3 provides a legend for reading the MIM notation. Throughout this review readers will see annotation labels in double square brackets and prefixed with a letter that refer to specific interactions in the MIM shown in Figure  1 and Additional file 2. We focus on aspects that alter the activity of these proteins, including: post-translational modifications, co-regulation, NAD + competition and co-regulated targets. Additionally, we discuss outstanding questions that would more accurately describe the relationship between these proteins.

HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
CHEBI:CHEBI:25367 = **molecule**     
CHEBI:CHEBI:25367 = **molecule**     
MESH:D011932 = **Reading**     
HGNC:20443 = **MTSS1**     
MESH:D016454 = **Review**     
MESH:D016422 = **Letter**     
HGNC:20443 = **MTSS1**     
GO:GO:0043687 = **post-translational protein modification**     
CHEBI:CHEBI:13389 = **NAD**     

*We focus on aspects that alter the activity of these proteins, including: post-translational modifications, co-regulation, NAD+ competition and co-regulated targets.*
- `p(HGNC:SIRT1) reg p(HGNC:PARP1)`

*We focus on aspects that alter the activity of these proteins, including: post-translational modifications, co-regulation, NAD+ competition and co-regulated targets.*
- `a(CHEBI:NAD) reg complex(p(HGNC:SIRT1), p(HGNC:PARP1))`

*We focus on aspects that alter the activity of these proteins, including: post-translational modifications, co-regulation, NAD+ competition and co-regulated targets.*
- `bp(GO:"post-translational protein modification") reg p(HGNC:SIRT1)`

*We focus on aspects that alter the activity of these proteins, including: post-translational modifications, co-regulation, NAD+ competition and co-regulated targets.*
- `bp(GO:"post-translational protein modification") reg p(HGNC:PARP1)`



## Paragraph 6

Modular layout diagram of SIRT1 and PARP1 MIM. Arrows connecting modules indicate that a node starting in a module connects to a node in the target module.

HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
HGNC:20443 = **MTSS1**     

*Modular layout diagram of SIRT1 and PARP1 MIM indicates potential regulatory interaction*
- `p(HGNC:SIRT1) reg p(HGNC:PARP1)`

*Modular layout diagram suggests potential regulatory interaction involving MTSS1*
- `p(HGNC:MTSS1) reg p(HGNC:SIRT1)`



## Paragraph 7

Reference guide for the MIM notation.

HGNC:20443 = **MTSS1**     



## Paragraph 8

Sirtuins were originally discovered in yeast where the SIR (Silent Information Regulator) genes are necessary for the repression of silent mating-type loci . The mammalian family of sirtuins consists of 7 proteins, SIRT1-7, which are ubiquitously expressed. Three of the sirtuins, SIRT1, SIRT6, and SIRT7 localize to the nucleus, SIRT2 is mainly localized in the cytoplasm, while the remaining three sirtuins: SIRT3, SIRT4, and SIRT5 are found in the mitochondria . The members of the sirtuin family not only differ in cellular locations, but also in enzymatic function. SIRT1 and SIRT5 are primarily protein deacetylases, SIRT4 and SIRT6 are mono(ADP)-ribosyltransferases, and SIRT2 and SIRT3 exhibit both enzymatic activities; no clear functionality has been attributed to SIRT 7 . The conserved catalytic domain of sirtuins is capable of carrying out both deacetylation and ADP-ribosylation activities using NAD+, and it has been suggested that sirtuins may have the potential to carry out either enzymatic activity under the right conditions . This review will focus on SIRT1 (EC 3.5.1.-) a member of the sirtuin family that is expressed in many tissues and acts as a NAD + -dependent protein deacetylase . SIRT1 has been implicated in signaling pathways underlying various diseases, including: diabetes, cardiovascular disease, neurodegeneration, cancer, aging, and obesity .

MESH:D037761 = **Sirtuins**     
MESH:D015003 = **Yeasts**     
MESH:D012094 = **Repression, Psychology**     
MESH:D005190 = **Family**     
MESH:D037761 = **Sirtuins**     
MESH:D037761 = **Sirtuins**     
HGNC:14929 = **SIRT1**     
HGNC:14934 = **SIRT6**     
HGNC:14935 = **SIRT7**     
GO:GO:0005634 = **nucleus**     
HGNC:10886 = **SIRT2**     
HP:HP:0012838 = **Localized**     
GO:GO:0005737 = **cytoplasm**     
MESH:D037761 = **Sirtuins**     
HGNC:14931 = **SIRT3**     
HGNC:14932 = **SIRT4**     
HGNC:14933 = **SIRT5**     
GO:GO:0005739 = **mitochondrion**     
MESH:D037761 = **Sirtuins**     
MESH:D005190 = **Family**     
HGNC:14929 = **SIRT1**     
HGNC:14933 = **SIRT5**     
HGNC:14932 = **SIRT4**     
HGNC:14934 = **SIRT6**     
MESH:D007244 = **Infectious Mononucleosis**     
CHEBI:CHEBI:16761 = **ADP**     
HGNC:10886 = **SIRT2**     
HGNC:14931 = **SIRT3**     
MESH:D020476 = **Exhibition**     
MESH:D037761 = **Sirtuins**     
MESH:D020134 = **Catalytic Domain**     
MESH:D037761 = **Sirtuins**     
MESH:D000074744 = **ADP-Ribosylation**     
CHEBI:CHEBI:15846 = **NAD(+)**     
MESH:D037761 = **Sirtuins**     
MESH:D016454 = **Review**     
HGNC:14929 = **SIRT1**     
FPLX:Cadherin = **Cadherin**     
MESH:D037761 = **Sirtuins**     
MESH:D005190 = **Family**     
MESH:D014024 = **Tissues**     
CHEBI:CHEBI:13389 = **NAD**     
HGNC:14929 = **SIRT1**     
GO:GO:0007165 = **signal transduction**     
MESH:D004194 = **Disease**     
MESH:D003920 = **Diabetes Mellitus**     
MESH:D002318 = **Cardiovascular Diseases**     
MESH:D019636 = **Neurodegenerative Diseases**     
MESH:D009369 = **Neoplasms**     
MESH:D000375 = **Aging**     
MESH:D009765 = **Obesity**     



## Paragraph 9

PARP1 (EC 2.4.2.30) is an NAD + -dependent nuclear ADP-ribosyltransferase with three domains: a DNA binding domain (DBD), an auto-modification domain (AD), and a catalytic domain [[A1]] . The PARP family of proteins are involved in many processes, including: DNA damage response, cell death, cell cycle regulation, and telomere regulation . The main function of PARP1 is the formation of poly(ADP-ribose) (PAR) chains on itself and other proteins [[A2]] . PARP1 is a transcriptional co-activator where PAR acts as a signal helping to regulate transcription . PAR is quickly cleaved by poly (ADP-ribose) glycohydrolase (PARG) [[A3]] . PARP1 becomes highly activated by DNA strand breaks; electrostatic repulsion between the poly (ADP)-ribose (PAR) chains and DNA eventually leads to its catalytic inactivation .

HGNC:270 = **PARP1**     
FPLX:Cadherin = **Cadherin**     
CHEBI:CHEBI:13389 = **NAD**     
HGNC:270 = **PARP1**     
GO:GO:0003677 = **DNA binding**     
HGNC:13633 = **ADIPOQ**     
MESH:D020134 = **Catalytic Domain**     
HGNC:9969 = **RFC1**     
HGNC:270 = **PARP1**     
MESH:D005190 = **Family**     
GO:GO:0006974 = **DNA damage response**     
GO:GO:0008219 = **cell death**     
MESH:D016615 = **Telomere**     
HGNC:270 = **PARP1**     
CHEBI:CHEBI:8288 = **Poly(ADPribose)**     
HGNC:6201 = **JTB**     
HGNC:1260 = **CFAP410**     
HGNC:270 = **PARP1**     
HGNC:6201 = **JTB**     
GO:GO:0006351 = **DNA-templated transcription**     
HGNC:6201 = **JTB**     
CHEBI:CHEBI:16960 = **ADP-D-ribose**     
MESH:D006026 = **Glycoside Hydrolases**     
HGNC:8605 = **PARG**     
HGNC:11647 = **TCIRG1**     
HGNC:270 = **PARP1**     
CHEBI:CHEBI:16991 = **deoxyribonucleic acid**     
CHEBI:CHEBI:16761 = **ADP**     
CHEBI:CHEBI:33942 = **ribose**     
HGNC:6201 = **JTB**     
CHEBI:CHEBI:16991 = **deoxyribonucleic acid**     

*PARP1 (EC 2.4.2.30) is an NAD + -dependent nuclear ADP-ribosyltransferase with three domains: a DNA binding domain (DBD), an auto-modification domain (AD), and a catalytic domain*
- `p(HGNC:PARP1, ma(GO:"DNA binding")) hasActivity ma(GO:"DNA binding")`

*The PARP family of proteins are involved in many processes, including: DNA damage response, cell death, cell cycle regulation, and telomere regulation*
- `p(HGNC:PARP1) increases bp(GO:"DNA damage response")`

*The PARP family of proteins are involved in many processes, including: DNA damage response, cell death, cell cycle regulation, and telomere regulation*
- `p(HGNC:PARP1) increases bp(GO:"cell death")`

*The PARP family of proteins are involved in many processes, including: DNA damage response, cell death, cell cycle regulation, and telomere regulation*
- `p(HGNC:PARP1) increases bp(GO:"cell cycle regulation")`

*The PARP family of proteins are involved in many processes, including: DNA damage response, cell death, cell cycle regulation, and telomere regulation*
- `p(HGNC:PARP1) increases bp(GO:"telomere regulation")`

*The main function of PARP1 is the formation of poly(ADP-ribose) (PAR) chains on itself and other proteins*
- `p(HGNC:PARP1) hasActivity rxn(reactants(a(CHEBI:NAD)), products(a(CHEBI:"Poly(ADPribose)")))`

*PARP1 is a transcriptional co-activator where PAR acts as a signal helping to regulate transcription*
- `p(HGNC:PARP1) increases bp(GO:"DNA-templated transcription")`

*PAR is quickly cleaved by poly (ADP-ribose) glycohydrolase (PARG)*
- `p(HGNC:PARG) decreases a(CHEBI:"Poly(ADPribose)")`

*PARP1 becomes highly activated by DNA strand breaks*
- `bp(GO:"DNA damage") increases act(p(HGNC:PARP1))`



## Paragraph 10

Post-transcriptional regulation of SIRT1 and PARP1

HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     

*Post-transcriptional regulation of SIRT1 and PARP1*
- `r(HGNC:SIRT1) regulates p(HGNC:PARP1)`



## Paragraph 11

Here we review post-translational modifications that affect the activities of SIRT1 and PARP1.

MESH:D016454 = **Review**     
GO:GO:0043687 = **post-translational protein modification**     
MESH:D000339 = **Affect**     
HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     

*Here we review post-translational modifications that affect the activities of SIRT1 and PARP1.*
- `bp(GO:"post-translational protein modification") regulates act(p(HGNC:SIRT1))`

*Here we review post-translational modifications that affect the activities of SIRT1 and PARP1.*
- `bp(GO:"post-translational protein modification") regulates act(p(HGNC:PARP1))`



## Paragraph 12

For a comprehensive review of sirtuin modifications, see Flick and Luscher . Below we describe several of these modifications for SIRT1 and augment this list with additional modifications.

MESH:D016454 = **Review**     
MESH:D037761 = **Sirtuins**     
HGNC:14929 = **SIRT1**     

*Below we describe several of these modifications for SIRT1*
- `p(HGNC:SIRT1) hasActivity ma(GO:"protein deacetylase activity")`



## Paragraph 13

SIRT1 phosphorylation results in both stimulatory and inhibitory effects. Phosphorylation of SIRT1 by JNK occurs at three sites: S27, S47, and T530 in response to oxidative stress that stimulates its deacetylation activity [[A4]] . In contrast, mTOR also phosphorylates SIRT1 in response to oxidative stress, but only at a single site, S47, resulting in the inhibition of SIRT1 [[A5]] suggesting a multi-site phosphorylation regulatory mechanism is in place; such a mechanism may be involved in the regulation of the timing of SIRT1 activity . CK2 phosphorylates human SIRT1 at S659 and S661, both in vivo and in vitro, stimulating its deacetylation activity [[A4]] . These two phosphorylation sites exist in a region of SIRT1 that are essential for SIRT1 activity both for its catalytic activity and ability to bind to substrates . Cyclin B/Cdk1, a cell cycle-dependent kinase, can phosphorylate SIRT1 at T530 and S540 [[A6]]. Phosphorylation at these two sites decreases the activity of SIRT1 and disrupts progress of the cell cycle . Similar to the case with mTOR and S47, T530 is a site phosphorylated by JNK and may also function as a part of a combinatorial modification program.

HGNC:14929 = **SIRT1**     
HGNC:14929 = **SIRT1**     
FPLX:JNK = **JNK**     
HGNC:10416 = **RPS27**     
GO:GO:0006979 = **response to oxidative stress**     
HGNC:9087 = **PLP2**     
HGNC:3942 = **MTOR**     
HGNC:14929 = **SIRT1**     
GO:GO:0006979 = **response to oxidative stress**     
HGNC:14929 = **SIRT1**     
HGNC:14929 = **SIRT1**     
FPLX:CK2 = **CK2**     
MESH:D006801 = **Humans**     
HGNC:14929 = **SIRT1**     
HGNC:9087 = **PLP2**     
HGNC:14929 = **SIRT1**     
HGNC:14929 = **SIRT1**     
GO:GO:0003824 = **catalytic activity**     
FPLX:Cyclin = **Cyclin**     
MESH:D010770 = **Phosphotransferases**     
HGNC:14929 = **SIRT1**     
HGNC:9620 = **TWF1**     
HGNC:14929 = **SIRT1**     
HGNC:3942 = **MTOR**     
FPLX:JNK = **JNK**     
MESH:D019542 = **Program**     

*Phosphorylation of SIRT1 by JNK occurs at three sites: S27, S47, and T530 in response to oxidative stress that stimulates its deacetylation activity*
- `p(FPLX:JNK, pmod(Ph, Ser, 27)) increases act(p(HGNC:SIRT1))`

*Phosphorylation of SIRT1 by JNK occurs at three sites: S27, S47, and T530 in response to oxidative stress that stimulates its deacetylation activity*
- `p(FPLX:JNK, pmod(Ph, Ser, 47)) increases act(p(HGNC:SIRT1))`

*mTOR also phosphorylates SIRT1 in response to oxidative stress, but only at a single site, S47, resulting in the inhibition of SIRT1*
- `p(HGNC:MTOR, pmod(Ph, Ser, 47)) decreases act(p(HGNC:SIRT1))`

*CK2 phosphorylates human SIRT1 at S659 and S661, both in vivo and in vitro, stimulating its deacetylation activity*
- `p(FPLX:CK2, pmod(Ph, Ser, 659)) increases act(p(HGNC:SIRT1))`

*CK2 phosphorylates human SIRT1 at S659 and S661, both in vivo and in vitro, stimulating its deacetylation activity*
- `p(FPLX:CK2, pmod(Ph, Ser, 661)) increases act(p(HGNC:SIRT1))`

*Cyclin B/Cdk1, a cell cycle-dependent kinase, can phosphorylate SIRT1 at T530 and S540*
- `complex(FPLX:Cyclin, p(MESH:Phosphotransferases)) decreases act(p(HGNC:SIRT1))`



## Paragraph 14

Kinases DYRK1A and DYRK3 have been shown to phosphorylate human SIRT1 at T522, stimulating the deacetylation of p53 by SIRT1[[A7]]; phosphorylation at this site increases the rate of product release by SIRT1 . AMPK phosphorylates human SIRT1 at T344 inhibiting its ability to decacetylate p53, a known target of SIRT1 [[A8]] . In addition to phosphorylation, methylation of SIRT1 by Set7/9 at K233, K235, K236, and K238 inhibits the SIRT1-mediated deacetylation of p53 in response to DNA damage [[A9]] . Sumoylation at K734 by SUMO1 increases, whereas desumoylation by SENP1 decreases, the activity of SIRT1 in response to genotoxic stress [[A10]] . In this study, genotoxic stress promoted the association of SIRT1 with SENP1, which may help to inhibit the ability of SIRT1 to promote survival. Additionally, transnitrosylation of SIRT1 by GAPDH at C387 and C390 has been found to inhibit the activity of SIRT1 leading to decreased PGC1alpha transcriptional activity; PGC1alpha is an important regulator of metabolism and mitochondrial function [[A11]] .

MESH:D010770 = **Phosphotransferases**     
HGNC:3091 = **DYRK1A**     
HGNC:3094 = **DYRK3**     
MESH:D006801 = **Humans**     
HGNC:14929 = **SIRT1**     
HGNC:11998 = **TP53**     
HGNC:14929 = **SIRT1**     
EFO:0002107 = **A7**     
HGNC:14929 = **SIRT1**     
FPLX:AMPK = **AMPK**     
MESH:D006801 = **Humans**     
HGNC:14929 = **SIRT1**     
HGNC:11998 = **TP53**     
HGNC:14929 = **SIRT1**     
HGNC:10732 = **SEMA4D**     
GO:GO:0032259 = **methylation**     
HGNC:14929 = **SIRT1**     
HGNC:30412 = **SETD7**     
HGNC:11998 = **TP53**     
MESH:D004249 = **DNA Damage**     
GO:GO:0016925 = **protein sumoylation**     
HGNC:12502 = **SUMO1**     
GO:GO:0016926 = **protein desumoylation**     
HGNC:17927 = **SENP1**     
HGNC:14929 = **SIRT1**     
GO:GO:0006974 = **DNA damage response**     
HGNC:5837 = **IGKV6D-21**     
MESH:D001244 = **Association**     
HGNC:14929 = **SIRT1**     
HGNC:17927 = **SENP1**     
HGNC:14929 = **SIRT1**     
MESH:D013534 = **Survival**     
HGNC:14929 = **SIRT1**     
HGNC:4141 = **GAPDH**     
HGNC:14929 = **SIRT1**     
HGNC:9237 = **PPARGC1A**     
HGNC:9237 = **PPARGC1A**     
GO:GO:0008152 = **metabolic process**     



## Paragraph 15

The activity of PARP1 can be modulated via post-translational modifications, including phosphorylation, sumoylation, and acetylation. DNA-PK phosphorylates PARP1 though its effect is unknown [[A12]] . Phosphorylation of PARP1 by AMPK has been shown to enhance its activity [[A13]] . This stimulation of PARP1 by AMPK contrasts with the AMPK-mediated inhibition of SIRT1 and suggests one mechanism by which AMPK, a metabolic sensor able to regulate ATP-consuming pathways, may be capable of controlling cell survival given the roles of PARP1 and SIRT1 in response to DNA damage. ERK1/2 has also been shown to phosphorylate PARP1 in neuronal cells and to stimulate the activity of PARP1 in response to DNA damage; inhibition of ERK1/2 results in the inhibition of PARP1-mediated cell death . PARP1 is acetylated by p300/CBP; this acetylation is involved in the activation of NF-kappaB by PARP1 [[A14]] . PARP1 is sumoylated by SUMO1 and SUMO3 at K486 of PARP1's auto-modification domain. This modification inhibits the ability of p300 to acetylate PARP1 and inhibits the expression of genes that are transcriptionally targeted by PARP1 [[A15]] .

HGNC:270 = **PARP1**     
GO:GO:0043687 = **post-translational protein modification**     
GO:GO:0016925 = **protein sumoylation**     
MESH:D000107 = **Acetylation**     
HGNC:9413 = **PRKDC**     
HGNC:270 = **PARP1**     
MESH:C040207 = **compound A 12**     
HGNC:270 = **PARP1**     
FPLX:AMPK = **AMPK**     
HGNC:270 = **PARP1**     
FPLX:AMPK = **AMPK**     
HGNC:14929 = **SIRT1**     
FPLX:AMPK = **AMPK**     
EFO:0001461 = **control**     
MESH:D013534 = **Survival**     
CHEBI:CHEBI:50906 = **role**     
HGNC:270 = **PARP1**     
HGNC:14929 = **SIRT1**     
MESH:D004249 = **DNA Damage**     
FPLX:ERK = **ERK**     
HGNC:270 = **PARP1**     
HGNC:270 = **PARP1**     
MESH:D004249 = **DNA Damage**     
FPLX:ERK = **ERK**     
GO:GO:0008219 = **cell death**     
HGNC:270 = **PARP1**     
MESH:D000107 = **Acetylation**     
FPLX:NFkappaB = **NFkappaB**     
HGNC:270 = **PARP1**     
HGNC:270 = **PARP1**     
HGNC:12502 = **SUMO1**     
HGNC:11124 = **SUMO3**     
HGNC:270 = **PARP1**     
HGNC:3373 = **EP300**     
HGNC:270 = **PARP1**     
HGNC:270 = **PARP1**     
HGNC:11854 = **TSPAN7**     

*DNA-PK phosphorylates PARP1 though its effect is unknown*
- `p(HGNC:PRKDC) reg p(HGNC:PARP1, pmod(Ph))`

*Phosphorylation of PARP1 by AMPK has been shown to enhance its activity*
- `p(FPLX:AMPK) increases act(p(HGNC:PARP1))`

*This stimulation of PARP1 by AMPK contrasts with the AMPK-mediated inhibition of SIRT1*
- `p(FPLX:AMPK) decreases act(p(HGNC:SIRT1))`

*ERK1/2 has also been shown to phosphorylate PARP1 in neuronal cells and to stimulate the activity of PARP1 in response to DNA damage*
- `p(FPLX:ERK) increases act(p(HGNC:PARP1))`

*PARP1 is acetylated by p300/CBP*
- `p(HGNC:EP300) increases p(HGNC:PARP1, pmod(Ac))`

*This acetylation is involved in the activation of NF-kappaB by PARP1*
- `p(HGNC:EP300) increases act(complex(p(FPLX:NFkappaB)))`

*PARP1 is sumoylated by SUMO1 and SUMO3 at K486 of PARP1's auto-modification domain*
- `p(HGNC:SUMO1, pmod(Sumo)) reg p(HGNC:PARP1)`

*PARP1 is sumoylated by SUMO1 and SUMO3 at K486 of PARP1's auto-modification domain*
- `p(HGNC:SUMO3, pmod(Sumo)) reg p(HGNC:PARP1)`

*This modification inhibits the ability of p300 to acetylate PARP1*
- `p(HGNC:PARP1, pmod(Sumo)) decreases act(p(HGNC:EP300))`



## Paragraph 16

Co-regulation of SIRT1 and PARP1

HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     

*Co-regulation of SIRT1 and PARP1*
- `p(HGNC:SIRT1) reg p(HGNC:PARP1)`



## Paragraph 17

Cross-modification and transcriptional co-regulation




## Paragraph 18

SIRT1 and PARP1 are transcriptionally and functionally interconnected . In SIRT1-deficient mouse cardiomyocytes, Rajamohan et al. in 2009 found increased levels of PARP1 acetylation in response to mechanical stress, suggesting that SIRT1 can deacetylate PARP1 [[A16]] . Whether this interaction occurs during genotoxic stress or other types of stresses remains an open question. No similar modification reaction has been seen on SIRT1 by PARP1 in response to DNA damage. However, SIRT1 is able to negatively regulate the PARP1 promoter, and the SIRT1 promoter has been shown to be under the influence of PARP2 .

HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
MESH:D051379 = **Mice**     
MESH:D032383 = **Myocytes, Cardiac**     
CHEBI:CHEBI:28984 = **aluminium atom**     
HGNC:270 = **PARP1**     
MESH:D000107 = **Acetylation**     
MESH:D013314 = **Stress, Mechanical**     
HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
MESH:D004249 = **DNA Damage**     
HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
HGNC:14929 = **SIRT1**     
HGNC:272 = **PARP2**     

*In SIRT1-deficient mouse cardiomyocytes, Rajamohan et al. in 2009 found increased levels of PARP1 acetylation in response to mechanical stress, suggesting that SIRT1 can deacetylate PARP1*
- `p(HGNC:SIRT1) decreases pmod(Ac, p(HGNC:PARP1))`

*SIRT1 is able to negatively regulate the PARP1 promoter*
- `p(HGNC:SIRT1) negativeCorrelation g(HGNC:PARP1)`

*the SIRT1 promoter has been shown to be under the influence of PARP2*
- `p(HGNC:PARP2) regulates g(HGNC:SIRT1)`



## Paragraph 19

Another key co-regulatory mechanism between these two proteins is the utilization of nicotinamide adenine dinucleotide (NAD+). It has been suggested by several studies that activation of PARP1 causes a depletion in NAD + levels, which inhibits SIRT1 activity . In mammals, NAD + is mainly generated through the salvage pathway; this pathway involves nicotinamide (NAM) as the major precursor in this multi-step process that involves the conversion of NAM into nicotinamide mononucleotide (NMN) and then NMN into NAD+. The rate-limiting protein in the NAM-NMN-NAD + conversion is nicotinamide phosphoribosyltransferase (NAMPT) [[A17]]. PARP1 was shown to have a greater effect on NAD + depletion than SIRT1 in response to the NAMPT inhibitor, FK866 . In a related study, the inhibition of NAMPT by FK866 was shown to produce an effect similar to SIRT1 depletion .

CHEBI:CHEBI:15846 = **NAD(+)**     
CHEBI:CHEBI:15846 = **NAD(+)**     
HGNC:270 = **PARP1**     
CHEBI:CHEBI:13389 = **NAD**     
HGNC:14929 = **SIRT1**     
MESH:D008322 = **Mammals**     
CHEBI:CHEBI:13389 = **NAD**     
CHEBI:CHEBI:34922 = **picloram**     
CHEBI:CHEBI:34922 = **picloram**     
CHEBI:CHEBI:17154 = **nicotinamide**     
EFO:0001651 = **precursor**     
CHEBI:CHEBI:50383 = **nicotinamide mononucleotide**     
CHEBI:CHEBI:16171 = **NMN zwitterion**     
CHEBI:CHEBI:16171 = **NMN zwitterion**     
CHEBI:CHEBI:15846 = **NAD(+)**     
HGNC:30092 = **NAMPT**     
HGNC:30092 = **NAMPT**     
MESH:C006022 = **A 17**     
HGNC:270 = **PARP1**     
CHEBI:CHEBI:13389 = **NAD**     
HGNC:14929 = **SIRT1**     
HGNC:30092 = **NAMPT**     
CHEBI:CHEBI:187413 = **FK-866**     
HGNC:30092 = **NAMPT**     
CHEBI:CHEBI:187413 = **FK-866**     
HGNC:14929 = **SIRT1**     

*activation of PARP1 causes a depletion in NAD + levels*
- `p(HGNC:PARP1) decreases a(CHEBI:"NAD(+)")`

*activation of PARP1 causes a depletion in NAD + levels, which inhibits SIRT1 activity*
- `p(HGNC:PARP1) decreases act(p(HGNC:SIRT1))`

*The rate-limiting protein in the NAM-NMN-NAD + conversion is nicotinamide phosphoribosyltransferase (NAMPT)*
- `p(HGNC:NAMPT) rateLimitingStepOf rxn(reactants(a(CHEBI:nicotinamide)), products(a(CHEBI:"nicotinamide mononucleotide")))`

*the inhibition of NAMPT by FK866*
- `a(CHEBI:FK-866) decreases act(p(HGNC:NAMPT))`

*the inhibition of NAMPT by FK866 was shown to produce an effect similar to SIRT1 depletion*
- `a(CHEBI:FK-866) causesNoChange act(p(HGNC:SIRT1))`



## Paragraph 20

Recent evidence suggests that local supplies of NAD + may be important for the enzymatic activities of these two proteins, shown in Figure  4. Nicotinamide mononucleotide adenylyltransferase 1 (NMNAT1), which catalyzes the conversion of NMN into NAD + in the synthesis of NAD + via the salvage pathway, can bind to (ADP-ribose) polymers in vitro leading to the stimulation of PARP1 activity; this effect is diminished when NMNAT1 is phosphorylated at S136 by protein kinase C (PKC) [[A18]] . A similar interaction has been shown to occur with SIRT1, whereby SIRT1 binds to NMNAT1 helping to recruit NMNAT1 to specific promoters, which may help stimulate SIRT1 activity [[A19]] . PARP1 activity leads to increased NAM concentrations at DNA damage sites, potentially leading to local inhibition of SIRT1 histone deacetylase activity . Further work is needed to understand the function of these two proteins around chromatin sites occupied beforehand by one of them.

CHEBI:CHEBI:13389 = **NAD**     
MESH:D009612 = **Nicotinamide-Nucleotide Adenylyltransferase**     
HGNC:17877 = **NMNAT1**     
CHEBI:CHEBI:16171 = **NMN zwitterion**     
CHEBI:CHEBI:13389 = **NAD**     
GO:GO:0009058 = **biosynthetic process**     
CHEBI:CHEBI:13389 = **NAD**     
CHEBI:CHEBI:34922 = **picloram**     
CHEBI:CHEBI:16960 = **ADP-D-ribose**     
CHEBI:CHEBI:60027 = **polymer**     
HGNC:270 = **PARP1**     
HGNC:17877 = **NMNAT1**     
MESH:D010770 = **Phosphotransferases**     
FPLX:PKC = **PKC**     
HGNC:14929 = **SIRT1**     
HGNC:14929 = **SIRT1**     
HGNC:17877 = **NMNAT1**     
HGNC:17877 = **NMNAT1**     
HGNC:14929 = **SIRT1**     
MESH:C039200 = **A 19**     
HGNC:270 = **PARP1**     
MESH:D004249 = **DNA Damage**     
HGNC:14929 = **SIRT1**     
GO:GO:0004407 = **histone deacetylase activity**     
MESH:D014937 = **Work**     
GO:GO:0000785 = **chromatin**     

*Nicotinamide mononucleotide adenylyltransferase 1 (NMNAT1), which catalyzes the conversion of NMN into NAD + in the synthesis of NAD + via the salvage pathway*
- `p(HGNC:NMNAT1) hasActivity ma(GO:"adenylyltransferase activity")`

*NMNAT1 can bind to (ADP-ribose) polymers in vitro leading to the stimulation of PARP1 activity; this effect is diminished when NMNAT1 is phosphorylated at S136 by protein kinase C (PKC)*
- `p(HGNC:NMNAT1, pmod(Ph, Ser, 136)) decreases act(p(HGNC:PARP1))`

*SIRT1 binds to NMNAT1 helping to recruit NMNAT1 to specific promoters, which may help stimulate SIRT1 activity*
- `complex(p(HGNC:NMNAT1), p(HGNC:SIRT1)) increases act(p(HGNC:SIRT1))`

*PARP1 activity leads to increased NAM concentrations at DNA damage sites*
- `act(p(HGNC:PARP1)) increases a(CHEBI:nicotinamide)`

*potentially leading to local inhibition of SIRT1 histone deacetylase activity*
- `a(CHEBI:nicotinamide) decreases act(p(HGNC:SIRT1), ma(GO:"histone deacetylase activity"))`



## Paragraph 21

The effect of NMNAT1 binding on SIRT1 and PARP1 activity. Zhang et al. proposed that NMNAT1 may stimulate SIRT1 activity; indicated by the dashed line.

HGNC:17877 = **NMNAT1**     
HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
CHEBI:CHEBI:28984 = **aluminium atom**     
HGNC:17877 = **NMNAT1**     
HGNC:14929 = **SIRT1**     

*Zhang et al. proposed that NMNAT1 may stimulate SIRT1 activity; indicated by the dashed line.*
- `p(HGNC:NMNAT1) increases act(p(HGNC:SIRT1))`



## Paragraph 22

Regulation of common SIRT1 and PARP1 targets

HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     

*Regulation of common SIRT1 and PARP1 targets*
- `p(HGNC:SIRT1) regulates p(HGNC:PARP1)`



## Paragraph 23

SIRT1/PARP1 response to DNA damage

MESH:D004249 = **DNA Damage**     

*SIRT1/PARP1 response to DNA damage*
- `p(HGNC:SIRT1) reg bp(MESH:"DNA Damage")`

*SIRT1/PARP1 response to DNA damage*
- `p(HGNC:PARP1) reg bp(MESH:"DNA Damage")`



## Paragraph 24

DNA damage response to both endogenous and exogenous sources is an intricate process that is not fully understood due to the complexity of the potential lesions, the number of proteins involved in both surveillance and repair, the interconnected regulation of proteins involved in the detection and repair of damage, stoppage of the cell cycle, and the potential induction of cell death; reviewed by . SIRT1 and PARP1 play several roles throughout the response to DNA damage from the initial response to final cell fate decisions.

GO:GO:0006974 = **DNA damage response**     
GO:GO:0008219 = **cell death**     
HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
CHEBI:CHEBI:50906 = **role**     
MESH:D004249 = **DNA Damage**     

*SIRT1 and PARP1 play several roles throughout the response to DNA damage from the initial response to final cell fate decisions.*
- `p(HGNC:SIRT1) reg bp(GO:"DNA damage response")`

*SIRT1 and PARP1 play several roles throughout the response to DNA damage from the initial response to final cell fate decisions.*
- `p(HGNC:PARP1) reg bp(GO:"DNA damage response")`

*DNA damage response is an intricate process that may potentially induce cell death*
- `bp(GO:"DNA damage response") reg bp(GO:"cell death")`



## Paragraph 25

Both SIRT1 and PARP1 are known to modify histones; deacetylation of histones triggers chromatin compaction and the inhibition of transcription, whereas poly (ADP-ribose) polymers help to relax chromatin. SIRT1 is capable of deacetylating several histone amino acid residues, including H1K26, H3K9, H3K14, and H4K16 [[A20]] , while PARP1 can modify histones H1, H2AK13, H2BK30, H3K27, H3K37, and H4K16 to possibly regulate transcription [[A21]] . It has been suggested that ADP-ribosylation of histone H1 promotes transcription by inhibiting the ability of histone H1 to bind to DNA . Additionally, a competitive interaction has been shown between acetylation and PAR where acetylation of H4K16 inhibits the ADP-ribosylation of histone H4 [[A22]] . Here a potential contradiction in the role of SIRT1 in condensing chromatin arises whereby SIRT1 deacetylation activity could potentially help drive the PARP1 ADP-ribosylation activity on H4K16. Currently, it is known that SIRT1 plays a role in DNA damage repair via histone deacetylation through the deacetylation of the two histone acetyltransferases, TIP60 and MOF, which are able to acetylate histone H4 [[A23]]. Deacetylation of these two proteins promotes their ubiquitin-dependent degradation affecting DNA double-strand break (DSB) repair either through the repression of repair or affecting the choice of repair mechanism (i.e. homologous recombination or non-homologous end joining (NHEJ)) . TIP60-dependent acetylation of H4K16 inhibits the binding of 53BP1 to H4K20me2, which promotes non-homologous end joining [[A24]] . Further studies are needed to understand how DNA damage might affect modifications on the various histones though it is known that genotoxic stress causes a random redistribution of SIRT1 across the genome with a correlated increase in levels of H1K26 acetylation . However, while PARP1 does localize to DNA strand breaks, it is also not known whether there is any further global redistribution PARP1 or a relationship to the redistribution of SIRT1.

HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
FPLX:Histone = **Histone**     
FPLX:Histone = **Histone**     
GO:GO:0000785 = **chromatin**     
GO:GO:0006351 = **DNA-templated transcription**     
CHEBI:CHEBI:16960 = **ADP-D-ribose**     
CHEBI:CHEBI:60027 = **polymer**     
GO:GO:0000785 = **chromatin**     
HGNC:14929 = **SIRT1**     
FPLX:Histone = **Histone**     
CHEBI:CHEBI:33708 = **amino-acid residue**     
HGNC:11896 = **TNFAIP3**     
HGNC:270 = **PARP1**     
FPLX:Histone = **Histone**     
HGNC:13518 = **CLIC4**     
GO:GO:0006351 = **DNA-templated transcription**     
MESH:D000074744 = **ADP-Ribosylation**     
FPLX:Histone_H1 = **Histone_H1**     
GO:GO:0006351 = **DNA-templated transcription**     
FPLX:Histone_H1 = **Histone_H1**     
CHEBI:CHEBI:16991 = **deoxyribonucleic acid**     
MESH:D000107 = **Acetylation**     
HGNC:6201 = **JTB**     
MESH:D000107 = **Acetylation**     
MESH:D000074744 = **ADP-Ribosylation**     
FPLX:Histone_H4 = **Histone_H4**     
HGNC:14929 = **SIRT1**     
GO:GO:0000785 = **chromatin**     
HGNC:14929 = **SIRT1**     
MESH:D004328 = **Drive**     
HGNC:270 = **PARP1**     
MESH:D000074744 = **ADP-Ribosylation**     
HGNC:14929 = **SIRT1**     
MESH:D004249 = **DNA Damage**     
FPLX:Histone = **Histone**     
MESH:D051548 = **Histone Acetyltransferases**     
HGNC:5275 = **KAT5**     
HGNC:17933 = **KAT8**     
FPLX:Histone_H4 = **Histone_H4**     
GO:GO:0009056 = **catabolic process**     
CHEBI:CHEBI:16991 = **deoxyribonucleic acid**     
MESH:D053903 = **DNA Breaks, Double-Stranded**     
MESH:D012094 = **Repression, Psychology**     
GO:GO:0035825 = **homologous recombination**     
HGNC:3349 = **ENG**     
GO:GO:0006303 = **double-strand break repair via nonhomologous end joining**     
MESH:D000107 = **Acetylation**     
HGNC:11999 = **TP53BP1**     
HGNC:3349 = **ENG**     
MESH:D004249 = **DNA Damage**     
MESH:D000339 = **Affect**     
FPLX:Histone = **Histone**     
EFO:0010216 = **random**     
HGNC:14929 = **SIRT1**     
EFO:0004420 = **genome**     
MESH:D000107 = **Acetylation**     
HGNC:270 = **PARP1**     
CHEBI:CHEBI:16991 = **deoxyribonucleic acid**     
HGNC:270 = **PARP1**     
HGNC:14929 = **SIRT1**     

*SIRT1 is capable of deacetylating several histone amino acid residues, including H1K26, H3K9, H3K14, and H4K16*
- `p(HGNC:SIRT1) decreases pmod(Ac, complex(FPLX:Histone))`

*PARP1 can modify histones H1, H2AK13, H2BK30, H3K27, H3K37, and H4K16 to possibly regulate transcription*
- `p(HGNC:PARP1) increases pmod(ADPRib, complex(FPLX:Histone))`

*ADP-ribosylation of histone H1 promotes transcription by inhibiting the ability of histone H1 to bind to DNA*
- `pmod(ADPRib, complex(FPLX:Histone_H1)) increases bp(GO:"DNA-templated transcription")`

*A competitive interaction has been shown between acetylation and PAR where acetylation of H4K16 inhibits the ADP-ribosylation of histone H4*
- `pmod(Ac, p(FPLX:Histone_H4), "K16") decreases pmod(ADPRib, p(FPLX:Histone_H4), "K16")`

*SIRT1 plays a role in DNA damage repair via histone deacetylation through the deacetylation of the histone acetyltransferase TIP60*
- `p(HGNC:SIRT1) decreases p(HGNC:KAT5)`

*SIRT1 plays a role in DNA damage repair via histone deacetylation through the deacetylation of the histone acetyltransferase MOF*
- `p(HGNC:SIRT1) decreases p(HGNC:KAT8)`

*TIP60-dependent acetylation of H4K16 inhibits the binding of 53BP1 to H4K20me2, which promotes non-homologous end joining*
- `p(HGNC:KAT5, pmod(Ac, p(FPLX:Histone_H4), "K16")) decreases bp(GO:"double-strand break repair via nonhomologous end joining")`



## Paragraph 26

DNA damage signaling pathway

MESH:D004249 = **DNA Damage**     
GO:GO:0007165 = **signal transduction**     

*DNA damage signaling pathway*
- `bp(GO:"signal transduction") regulates bp(MESH:"DNA Damage")`



## Paragraph 27

Both SIRT1 and PARP1 are DNA damage responders and the absence of either of these proteins may lead to DNA damage sensitization . PARP1 begins to localize to DNA breaks rapidly and becomes activated by binding to DNA breaks. The ADP-ribosylation activity of PARP1 increases 10-500 fold as a result of binding to DNA breaks [[A25]] . Once activated, PARP1 may help repair single strand DNA breaks, preventing their conversion to double-stranded breaks [[A26]] . In addition, PARP1 is involved in DNA repair through its associations with base excision repair (BER) enzymes such as polymerase beta, XRCC1 and DNA ligase III by helping these proteins localize to sites of DNA damage [[A27]] .

HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
MESH:D004249 = **DNA Damage**     
MESH:D004249 = **DNA Damage**     
GO:GO:0046960 = **sensitization**     
HGNC:270 = **PARP1**     
MESH:D053960 = **DNA Breaks**     
MESH:D053960 = **DNA Breaks**     
MESH:D000074744 = **ADP-Ribosylation**     
HGNC:270 = **PARP1**     
MESH:D053960 = **DNA Breaks**     
HGNC:270 = **PARP1**     
MESH:D053904 = **DNA Breaks, Single-Stranded**     
HGNC:5836 = **IGKV6-21**     
HGNC:270 = **PARP1**     
GO:GO:0006281 = **DNA repair**     
MESH:D001244 = **Association**     
CHEBI:CHEBI:22695 = **base**     
MESH:D000097147 = **Excision Repair**     
GO:GO:0006284 = **base-excision repair**     
MESH:D004798 = **Enzymes**     
HGNC:12828 = **XRCC1**     
HGNC:6600 = **LIG3**     
MESH:D004249 = **DNA Damage**     

*Both SIRT1 and PARP1 are DNA damage responders and the absence of either of these proteins may lead to DNA damage sensitization.*
- `p(HGNC:SIRT1) reg bp(GO:"DNA repair")`

*Both SIRT1 and PARP1 are DNA damage responders and the absence of either of these proteins may lead to DNA damage sensitization.*
- `p(HGNC:PARP1) reg bp(GO:"DNA repair")`

*The ADP-ribosylation activity of PARP1 increases 10-500 fold as a result of binding to DNA breaks.*
- `p(HGNC:PARP1) increases act(p(HGNC:PARP1), ma(ADP-ribosylation))`

*Once activated, PARP1 may help repair single strand DNA breaks, preventing their conversion to double-stranded breaks.*
- `p(HGNC:PARP1) decreases bp(MESH:"DNA Breaks, Single-Stranded")`

*PARP1 is involved in DNA repair through its associations with base excision repair (BER) enzymes such as polymerase beta, XRCC1 and DNA ligase III by helping these proteins localize to sites of DNA damage.*
- `p(HGNC:PARP1) hasActivity ma(GO:"base-excision repair")`



## Paragraph 28

Two early responders of DNA damage linked to SIRT1 and PARP1 regulation are ATM (ataxia telangiectasia, mutated) and CHK2 (checkpoint kinase 2) . The activation of ATM by DNA breaks requires the activation of the MRE11-RAD50-NBS1 (MRN) complex [[A28-A30]]. It has been shown that PARP1 binds to ATM, an interaction that is stimulated by DNA damage, and that the automodification of PARP1 leads to ATM activation [[A31]] .

MESH:D004249 = **DNA Damage**     
HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
HGNC:795 = **ATM**     
MESH:D001260 = **Ataxia Telangiectasia**     
HGNC:16627 = **CHEK2**     
HGNC:16627 = **CHEK2**     
HGNC:795 = **ATM**     
MESH:D053960 = **DNA Breaks**     
HGNC:270 = **PARP1**     
HGNC:795 = **ATM**     
MESH:D004249 = **DNA Damage**     
HGNC:270 = **PARP1**     
HGNC:795 = **ATM**     

*The activation of ATM by DNA breaks requires the activation of the MRE11-RAD50-NBS1 (MRN) complex*
- `complex(p(HGNC:MRE11), p(HGNC:RAD50), p(HGNC:NBS1)) increases act(p(HGNC:ATM))`

*PARP1 binds to ATM, an interaction that is stimulated by DNA damage, and that the automodification of PARP1 leads to ATM activation*
- `p(HGNC:PARP1) increases act(p(HGNC:ATM))`



## Paragraph 29

An extended feedback loop has been proposed by Gorospe and de Cabo involving SIRT1 and several key DNA damage repair proteins . In this loop, NBS1 is phosphorylated by ATM in response to genotoxic stress at S343 for the activation of NBS1; to be phosphorylated, it is necessary for NBS1 to be in a hypoacetylated state, which SIRT1 helps to maintain by deacetylating NBS1 [[A32-A33]] . CHK2 is activated when T68 is phosphorylated by ATM. CHK2 can then phosphorylate HuR at several sites causing it to dissociate from SIRT1 mRNA, and thereby reduce the half-life of the SIRT1 mRNA [[A34]] . It has been suggested that in repairable DNA damage situations SIRT1 levels are elevated leading to a survival response, but during lethal DNA damage SIRT1 levels can be attenuated by CHK2 through the phosphorylation of HuR that can ultimately result in cell death .

MESH:D005246 = **Feedback**     
HGNC:14929 = **SIRT1**     
MESH:D004249 = **DNA Damage**     
HGNC:7652 = **NBN**     
HGNC:795 = **ATM**     
GO:GO:0006974 = **DNA damage response**     
HGNC:7652 = **NBN**     
HGNC:7652 = **NBN**     
HGNC:14929 = **SIRT1**     
HGNC:7652 = **NBN**     
HGNC:16627 = **CHEK2**     
HGNC:795 = **ATM**     
HGNC:16627 = **CHEK2**     
HGNC:3312 = **ELAVL1**     
HGNC:14929 = **SIRT1**     
CHEBI:CHEBI:33699 = **messenger RNA**     
MESH:D006207 = **Half-Life**     
HGNC:14929 = **SIRT1**     
CHEBI:CHEBI:33699 = **messenger RNA**     
MESH:D004249 = **DNA Damage**     
HGNC:14929 = **SIRT1**     
MESH:D013534 = **Survival**     
MESH:D004249 = **DNA Damage**     
HGNC:14929 = **SIRT1**     
HGNC:16627 = **CHEK2**     
HGNC:3312 = **ELAVL1**     
GO:GO:0008219 = **cell death**     

*NBS1 is phosphorylated by ATM in response to genotoxic stress at S343 for the activation of NBS1*
- `p(HGNC:ATM) increases p(HGNC:NBN, pmod(Ph, Ser, 343))`

*SIRT1 helps to maintain NBS1 in a hypoacetylated state by deacetylating NBS1*
- `p(HGNC:SIRT1) decreases p(HGNC:NBN, pmod(Ac))`

*CHK2 is activated when T68 is phosphorylated by ATM*
- `p(HGNC:ATM) increases p(HGNC:CHEK2, pmod(Ph, Thr, 68))`

*CHK2 can phosphorylate HuR causing it to dissociate from SIRT1 mRNA, and thereby reduce the half-life of the SIRT1 mRNA*
- `p(HGNC:CHEK2) decreases r(HGNC:SIRT1)`

*In repairable DNA damage situations SIRT1 levels are elevated leading to a survival response*
- `bp(GO:"DNA damage response") increases p(HGNC:SIRT1)`

*During lethal DNA damage SIRT1 levels can be attenuated by CHK2 through the phosphorylation of HuR*
- `p(HGNC:CHEK2) decreases p(HGNC:SIRT1)`

*During lethal DNA damage SIRT1 levels can be attenuated by CHK2 through the phosphorylation of HuR that can ultimately result in cell death*
- `p(HGNC:CHEK2) increases bp(GO:"cell death")`



## Paragraph 30

SIRT1 is also regulated by c-MYC and E2F1, two proteins involved in cell proliferation, differentiation and apoptosis, through negative feedback loops shown in Figure  5. E2F1, a transcription factor, induces the transcription of SIRT1 [[A35]]. Conversely, E2F1 has been suggested to be a target for SIRT1 deacetylation, which inhibits E2F1 activity [[A36-A37]] . Additionally, the transcriptional activity of E2F1 is inhibited by Retinoblastoma (Rb), which is another substrate of SIRT1 deacetylation; acetylation of Rb has been shown to regulate the binding of Rb to E2F1 [[A38]] . Two studies have examined the interactions between SIRT1 and c-MYC producing contradictory results. In one publication, c-MYC over-expression leads to an increase in SIRT1 expression and then deacetylation of c-MYC by SIRT1 leads to the destabilization of c-MYC [[A39]] . In the second publication, neither the induction of SIRT1 expression nor the destabilization of c-MYC was seen following c-MYC activation. Instead, a stabilizing effect on c-MYC due to deacetylation by SIRT1 was found. Also in the second study, Menssen et al. found that c-MYC can induce the transcription of NAMPT and help sequester DBC1, an inhibitor of SIRT1 [[A40]] . Another line of evidence suggesting that SIRT1 may affect NAMPT through a second mechanism involving the circadian clock will be discussed later. There is evidence that PARP1 binds to E2F1 stimulating E2F1-dependent transcription of c-MYC [[A41]] . This presents the possibility that both SIRT1 and PARP1 may be capable of influencing the regulation of NAMPT to affect NAD + levels through c-MYC.

HGNC:14929 = **SIRT1**     
HGNC:7553 = **MYC**     
HGNC:3113 = **E2F1**     
GO:GO:0008283 = **cell population proliferation**     
GO:GO:0030154 = **cell differentiation**     
GO:GO:0006915 = **apoptotic process**     
MESH:D005246 = **Feedback**     
HGNC:3113 = **E2F1**     
MESH:D014157 = **Transcription Factors**     
GO:GO:0006351 = **DNA-templated transcription**     
HGNC:14929 = **SIRT1**     
HGNC:3113 = **E2F1**     
HGNC:14929 = **SIRT1**     
HGNC:3113 = **E2F1**     
HGNC:3113 = **E2F1**     
MESH:D012175 = **Retinoblastoma**     
HGNC:9884 = **RB1**     
EFO:0005061 = **substrate**     
HGNC:14929 = **SIRT1**     
MESH:D000107 = **Acetylation**     
HGNC:9884 = **RB1**     
HGNC:9884 = **RB1**     
HGNC:3113 = **E2F1**     
HGNC:14929 = **SIRT1**     
HGNC:7553 = **MYC**     
MESH:D011642 = **Publications**     
HGNC:7553 = **MYC**     
HGNC:14929 = **SIRT1**     
HGNC:7553 = **MYC**     
HGNC:14929 = **SIRT1**     
HGNC:7553 = **MYC**     
MESH:D011642 = **Publications**     
HGNC:14929 = **SIRT1**     
HGNC:7553 = **MYC**     
HGNC:7553 = **MYC**     
HGNC:7553 = **MYC**     
HGNC:14929 = **SIRT1**     
CHEBI:CHEBI:28984 = **aluminium atom**     
HGNC:7553 = **MYC**     
GO:GO:0006351 = **DNA-templated transcription**     
HGNC:30092 = **NAMPT**     
HGNC:23360 = **CCAR2**     
HGNC:14929 = **SIRT1**     
HGNC:14929 = **SIRT1**     
MESH:D000339 = **Affect**     
HGNC:30092 = **NAMPT**     
MESH:D057906 = **Circadian Clocks**     
HGNC:270 = **PARP1**     
HGNC:3113 = **E2F1**     
GO:GO:0006351 = **DNA-templated transcription**     
HGNC:7553 = **MYC**     
HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
HGNC:30092 = **NAMPT**     
MESH:D000339 = **Affect**     
CHEBI:CHEBI:13389 = **NAD**     
HGNC:7553 = **MYC**     

*E2F1, a transcription factor, induces the transcription of SIRT1*
- `p(HGNC:E2F1) increases g(HGNC:SIRT1)`

*E2F1 has been suggested to be a target for SIRT1 deacetylation, which inhibits E2F1 activity*
- `p(HGNC:SIRT1) decreases act(p(HGNC:E2F1))`

*The transcriptional activity of E2F1 is inhibited by Retinoblastoma (Rb)*
- `p(HGNC:RB1) decreases act(p(HGNC:E2F1))`

*Rb is another substrate of SIRT1 deacetylation*
- `p(HGNC:SIRT1) decreases p(HGNC:RB1, pmod(Ac))`

*c-MYC over-expression leads to an increase in SIRT1 expression*
- `p(HGNC:MYC) increases g(HGNC:SIRT1)`

*Deacetylation of c-MYC by SIRT1 leads to the destabilization of c-MYC*
- `p(HGNC:SIRT1) decreases p(HGNC:MYC)`

*c-MYC can induce the transcription of NAMPT*
- `p(HGNC:MYC) increases g(HGNC:NAMPT)`

*PARP1 binds to E2F1 stimulating E2F1-dependent transcription of c-MYC*
- `p(HGNC:PARP1) increases act(p(HGNC:E2F1), ma(GO:"DNA-templated transcription"))`



## Paragraph 31

Interactions between SIRT1 and transcription factors c-MYC and E2F1. Solid lines between SIRT1 and c-MYC indicated are interactions from Yuan, Minter-Dykhouse et al. 2009 forming a negative feedback loop, while dashed lines are findings related to SIRT1 and c-MYC from Menssen, Hydbring et al. 2012.

HGNC:14929 = **SIRT1**     
MESH:D014157 = **Transcription Factors**     
HGNC:7553 = **MYC**     
HGNC:3113 = **E2F1**     
HGNC:14929 = **SIRT1**     
HGNC:7553 = **MYC**     
CHEBI:CHEBI:28984 = **aluminium atom**     
MESH:D005246 = **Feedback**     
HGNC:14929 = **SIRT1**     
HGNC:7553 = **MYC**     
CHEBI:CHEBI:28984 = **aluminium atom**     

*Solid lines between SIRT1 and c-MYC indicated are interactions from Yuan, Minter-Dykhouse et al. 2009 forming a negative feedback loop*
- `p(HGNC:SIRT1) negativeCorrelation p(HGNC:MYC)`

*Interactions between SIRT1 and transcription factors c-MYC and E2F1*
- `p(HGNC:SIRT1) reg p(HGNC:E2F1)`



## Paragraph 32

Another co-regulated protein is NF-kappaB, a regulator of cellular response, including inflammation, to stress. In the case of NF-kappaB, the effects of SIRT1 and PARP1 are opposing. SIRT1 can deacetylate the RelA/p65 subunit of NF-kappaB at K310 to inhibit NF-kappaB transactivation activity [[A42]] . PARP1 is an activator of NF-kappaB through its direct binding to NF-kappaB; acetylation of PARP1 by p300/CBP is required for the binding of PARP1 to NF-kappaB [[A43]] .

FPLX:NFkappaB = **NFkappaB**     
GO:GO:0006954 = **inflammatory response**     
FPLX:NFkappaB = **NFkappaB**     
HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
HGNC:14929 = **SIRT1**     
FPLX:NFkappaB = **NFkappaB**     
FPLX:NFkappaB = **NFkappaB**     
GO:GO:2000144 = **positive regulation of DNA-templated transcription initiation**     
HGNC:270 = **PARP1**     
CHEBI:CHEBI:195251 = **activator**     
FPLX:NFkappaB = **NFkappaB**     
FPLX:NFkappaB = **NFkappaB**     
MESH:D000107 = **Acetylation**     
HGNC:270 = **PARP1**     
HGNC:270 = **PARP1**     
FPLX:NFkappaB = **NFkappaB**     
HGNC:18027 = **POLR1F**     

*SIRT1 can deacetylate the RelA/p65 subunit of NF-kappaB at K310 to inhibit NF-kappaB transactivation activity*
- `p(HGNC:SIRT1) decreases act(complex(FPLX:NFkappaB), ma(GO:"positive regulation of DNA-templated transcription initiation"))`

*PARP1 is an activator of NF-kappaB through its direct binding to NF-kappaB*
- `p(HGNC:PARP1) increases act(complex(FPLX:NFkappaB), ma(GO:"positive regulation of DNA-templated transcription initiation"))`

*Acetylation of PARP1 by p300/CBP is required for the binding of PARP1 to NF-kappaB*
- `p(HGNC:PARP1, pmod(Ac)) increases complex(FPLX:NFkappaB)`



## Paragraph 33

Given the importance of p53 to apoptotic response, a number of studies have focused on the regulation of p53 by SIRT1. p53 acts as a transcription factor that induces apoptosis and is inhibited by SIRT1 deacetylation [[A44]] . SIRT1 has the capability of deacetylating p53 at several sites in mouse embryonic fibroblasts (MEFs) and SIRT1-deficient cells possess hyperacetylated p53; the precise role of p53 acetylation is unclear [[A45]] . Several proteins help to modify the interactions of SIRT1 with p53, including p53 (itself), DBC1, AROS, and HIC1, suggesting that it is a cellular imperative to control the inhibition of p53 by SIRT1 under certain conditions. p53 can repress SIRT1 expression during nutrient abundance via p53-binding sites on the SIRT1 promoter. This effect is countered by the transcription factor FOXO3A, which interacts with p53 in an inhibitory fashion during nutrient deprivation [[A46-A47]] . Hypermethylated in cancer-1 (HIC1) is a transcriptional repressor of the SIRT1 promoter [[A48]] that helps prevent age-dependent cancers in mice. If HIC1 is inhibited, SIRT1 expression increases, allowing for more efficient inactivation of p53; p53 over-expression leads to the transactivation of HIC1, thus creating a negative feedback loop .

HGNC:11998 = **TP53**     
HGNC:11998 = **TP53**     
HGNC:14929 = **SIRT1**     
HGNC:11998 = **TP53**     
MESH:D014157 = **Transcription Factors**     
GO:GO:0006915 = **apoptotic process**     
HGNC:14929 = **SIRT1**     
HGNC:14929 = **SIRT1**     
HGNC:11998 = **TP53**     
MESH:D051379 = **Mice**     
MESH:D005347 = **Fibroblasts**     
HGNC:11998 = **TP53**     
HGNC:11998 = **TP53**     
MESH:D000107 = **Acetylation**     
HGNC:14929 = **SIRT1**     
HGNC:11998 = **TP53**     
HGNC:11998 = **TP53**     
HGNC:23360 = **CCAR2**     
HGNC:28749 = **RPS19BP1**     
HGNC:4909 = **HIC1**     
HGNC:11998 = **TP53**     
HGNC:14929 = **SIRT1**     
HGNC:11998 = **TP53**     
HGNC:14929 = **SIRT1**     
CHEBI:CHEBI:33284 = **nutrient**     
HGNC:14929 = **SIRT1**     
MESH:D014157 = **Transcription Factors**     
HGNC:3821 = **FOXO3**     
HGNC:11998 = **TP53**     
CHEBI:CHEBI:33284 = **nutrient**     
HGNC:4909 = **HIC1**     
HGNC:14929 = **SIRT1**     
HGNC:7094 = **MICE**     
HGNC:4909 = **HIC1**     
HGNC:14929 = **SIRT1**     
HGNC:11998 = **TP53**     
HGNC:11998 = **TP53**     
GO:GO:2000144 = **positive regulation of DNA-templated transcription initiation**     
HGNC:4909 = **HIC1**     
MESH:D005246 = **Feedback**     

*p53 acts as a transcription factor that induces apoptosis and is inhibited by SIRT1 deacetylation*
- `p(HGNC:SIRT1) decreases act(p(HGNC:TP53), ma(GO:"transcription factor activity"))`

*SIRT1 has the capability of deacetylating p53 at several sites in mouse embryonic fibroblasts (MEFs) and SIRT1-deficient cells possess hyperacetylated p53*
- `p(HGNC:SIRT1) directlyDecreases p(HGNC:TP53, pmod(Ac))`

*p53 can repress SIRT1 expression during nutrient abundance via p53-binding sites on the SIRT1 promoter*
- `p(HGNC:TP53) decreases g(HGNC:SIRT1)`

*This effect is countered by the transcription factor FOXO3A, which interacts with p53 in an inhibitory fashion during nutrient deprivation*
- `p(HGNC:FOXO3) decreases act(p(HGNC:TP53), ma(GO:"transcription factor activity"))`

*Hypermethylated in cancer-1 (HIC1) is a transcriptional repressor of the SIRT1 promoter*
- `p(HGNC:HIC1) decreases g(HGNC:SIRT1)`

*p53 over-expression leads to the transactivation of HIC1, thus creating a negative feedback loop*
- `p(HGNC:TP53) increases g(HGNC:HIC1)`



## Paragraph 34

Micro-RNAs have also been shown to downregulate SIRT1-dependent deacetylation of p53. p53 can stimulate the expression of miRNA-34 [[A49]], which subsequently drives down the expression of SIRT1 lowering SIRT1 availability to inhibit p53. Over 15 micro-RNAs affect the expression of SIRT1 either directly or by decreasing the expression of HuR, which stabilizes SIRT1 mRNA [[A50]] .

MESH:D035683 = **MicroRNAs**     
HGNC:11998 = **TP53**     
HGNC:11998 = **TP53**     
MESH:D004328 = **Drive**     
HGNC:14929 = **SIRT1**     
HGNC:14929 = **SIRT1**     
HGNC:11998 = **TP53**     
MESH:D035683 = **MicroRNAs**     
MESH:D000339 = **Affect**     
HGNC:14929 = **SIRT1**     
HGNC:3312 = **ELAVL1**     
HGNC:14929 = **SIRT1**     
CHEBI:CHEBI:33699 = **messenger RNA**     

*Micro-RNAs have also been shown to downregulate SIRT1-dependent deacetylation of p53.*
- `m(MESH:D035683) decreases p(HGNC:SIRT1)`

*p53 can stimulate the expression of miRNA-34*
- `p(HGNC:TP53) increases m(HGNC:MIR34A)`

*p53 can stimulate the expression of miRNA-34 which subsequently drives down the expression of SIRT1 lowering SIRT1 availability to inhibit p53*
- `m(HGNC:MIR34A) decreases p(HGNC:SIRT1)`

*Over 15 micro-RNAs affect the expression of HuR*
- `m(MESH:D035683) decreases p(HGNC:ELAVL1)`

*HuR stabilizes SIRT1 mRNA*
- `p(HGNC:ELAVL1) increases r(HGNC:SIRT1)`



## Paragraph 35

Given the well-studied nature of p53 as a SIRT1 substrate, p53 has been used to characterize SIRT1 inhibitors and activators. In humans, deleted in breast cancer 1 (DBC1) acts as an inhibitor of SIRT1 (an inhibitory effect increased by the phosphorylation of DBC1) and whose effect has been shown to lead to p53 hypoacetylation [[A51-A52]] . Active Regulator of SIRT1 (AROS) has been shown to bind SIRT1 and help enhance the deacetylation of p53 by SIRT1 [[A53]] . Further studies are needed to understand if the effects on p53 acetylation states are specific to the activities of DBC1 and AROS on SIRT1 or if other substrates of these two proteins are involved.

MESH:D019368 = **Nature**     
HGNC:11998 = **TP53**     
HGNC:14929 = **SIRT1**     
EFO:0005061 = **substrate**     
HGNC:11998 = **TP53**     
CHEBI:CHEBI:90375 = **Sir1 inhibitor**     
MESH:D006801 = **Humans**     
HGNC:23360 = **CCAR2**     
HGNC:2687 = **BRINP1**     
HGNC:14929 = **SIRT1**     
HGNC:2687 = **BRINP1**     
HGNC:11998 = **TP53**     
HGNC:28749 = **RPS19BP1**     
HGNC:28749 = **RPS19BP1**     
HGNC:14929 = **SIRT1**     
HGNC:11998 = **TP53**     
HGNC:14929 = **SIRT1**     
HGNC:11998 = **TP53**     
MESH:D000107 = **Acetylation**     
HGNC:2687 = **BRINP1**     
HGNC:28749 = **RPS19BP1**     
HGNC:14929 = **SIRT1**     

*In humans, deleted in breast cancer 1 (DBC1) acts as an inhibitor of SIRT1*
- `p(HGNC:CCAR2) decreases act(p(HGNC:SIRT1))`

*an inhibitory effect increased by the phosphorylation of DBC1*
- `p(HGNC:CCAR2, pmod(Ph)) directlyDecreases act(p(HGNC:SIRT1))`

*whose effect has been shown to lead to p53 hypoacetylation*
- `p(HGNC:CCAR2) decreases pmod(p(HGNC:TP53), Ac)`

*Active Regulator of SIRT1 (AROS) has been shown to bind SIRT1 and help enhance the deacetylation of p53 by SIRT1*
- `p(HGNC:RPS19BP1) increases act(p(HGNC:SIRT1), ma(GO:"protein deacetylase activity"))`

*Active Regulator of SIRT1 (AROS) has been shown to bind SIRT1 and help enhance the deacetylation of p53 by SIRT1*
- `p(HGNC:RPS19BP1) increases deg(pmod(p(HGNC:TP53), Ac))`



## Paragraph 36

Much less is known about the interaction between PARP1 and p53. PARP1 helps p53 accumulate in the nucleus by (ADP-ribosyl)ating p53, which prevents p53 nuclear export , and there is evidence to suggest that SIRT1 deacetylation activity is capable of blocking p53 nuclear translocation .

HGNC:270 = **PARP1**     
HGNC:11998 = **TP53**     
HGNC:270 = **PARP1**     
HGNC:11998 = **TP53**     
GO:GO:0005634 = **nucleus**     
CHEBI:CHEBI:22259 = **adenosinediphosphoribosyl group**     
HGNC:11998 = **TP53**     
HGNC:11998 = **TP53**     
GO:GO:0051168 = **nuclear export**     
HGNC:14929 = **SIRT1**     
HGNC:11998 = **TP53**     
GO:GO:0051170 = **import into nucleus**     

*PARP1 helps p53 accumulate in the nucleus by (ADP-ribosyl)ating p53, which prevents p53 nuclear export*
- `p(HGNC:PARP1) increases tloc(p(HGNC:TP53), fromLoc(GO:"nuclear export"), toLoc(GO:nucleus))`

*there is evidence to suggest that SIRT1 deacetylation activity is capable of blocking p53 nuclear translocation*
- `p(HGNC:SIRT1) decreases tloc(p(HGNC:TP53), fromLoc(GO:"nuclear export"), toLoc(GO:nucleus))`



## Paragraph 37

In addition to the role that SIRT1 plays in the inhibition of p53, SIRT1 is capable of deacetylating Ku70 at K539 and K542; the acetylation of Ku70 leads to the dissociation of the Ku70 and Bax helping to trigger apoptosis; Bax is a pro-apoptotic factor that is sequestered by Ku70 [[A54-A55]] . NBS1, which we have discussed here beforehand as being activated via deacetylation by SIRT1, has also been shown to help control the interaction between Ku70 and Bax by stimulating the acetylation of Ku70 [[A56]] . The exact conditions leading to a differential role of SIRT1 on the Ku70 and Bax complex remains to be uncovered.

HGNC:14929 = **SIRT1**     
HGNC:11998 = **TP53**     
HGNC:14929 = **SIRT1**     
HGNC:4055 = **XRCC6**     
MESH:D000107 = **Acetylation**     
HGNC:4055 = **XRCC6**     
MESH:D004213 = **Dissociative Disorders**     
HGNC:4055 = **XRCC6**     
HGNC:959 = **BAX**     
GO:GO:0006915 = **apoptotic process**     
HGNC:959 = **BAX**     
HGNC:4055 = **XRCC6**     
HGNC:7652 = **NBN**     
HGNC:14929 = **SIRT1**     
HGNC:4055 = **XRCC6**     
HGNC:959 = **BAX**     
MESH:D000107 = **Acetylation**     
HGNC:4055 = **XRCC6**     
HGNC:14929 = **SIRT1**     
HGNC:4055 = **XRCC6**     
GO:GO:0097144 = **BAX complex**     

*In addition to the role that SIRT1 plays in the inhibition of p53*
- `p(HGNC:SIRT1) decreases act(p(HGNC:TP53))`

*SIRT1 is capable of deacetylating Ku70 at K539 and K542*
- `p(HGNC:SIRT1) directlyDecreases pmod(p(HGNC:XRCC6), Ac, K539)`

*SIRT1 is capable of deacetylating Ku70 at K539 and K542*
- `p(HGNC:SIRT1) directlyDecreases pmod(p(HGNC:XRCC6), Ac, K542)`

*the acetylation of Ku70 leads to the dissociation of the Ku70 and Bax helping to trigger apoptosis*
- `pmod(p(HGNC:XRCC6), Ac) increases complex(p(HGNC:XRCC6), p(HGNC:BAX))`

*Bax is a pro-apoptotic factor that is sequestered by Ku70*
- `complex(p(HGNC:XRCC6), p(HGNC:BAX)) decreases bp(GO:"apoptotic process")`

*NBS1, which we have discussed here beforehand as being activated via deacetylation by SIRT1, has also been shown to help control the interaction between Ku70 and Bax by stimulating the acetylation of Ku70*
- `p(HGNC:NBN) increases pmod(p(HGNC:XRCC6), Ac)`



## Paragraph 38

PARP1 plays a role in cell death pathways (apoptosis or necrosis) in the course of responding to DNA damage. ATP is required for optimal caspase activation, and the depletion of ATP can direct cells between apoptotic and necrotic pathways . During normal apoptosis, PARP1 is cleaved by caspases; the role of these cleaved fragments play is not fully understood [[A57]]. PARP1 cleavage helps prevent energy depletion (NAD + and ATP) in response to severe DNA damage; the extreme loss of NAD + triggers necrosis by reducing cellular ability to synthesize ATP [[A58]] . Cells with severe DNA damage die from necrosis because they are not able to switch away from the necrotic pathway since the kinetics of NAD + depletion are faster than those of PARP1 cleavage . Rapid depletion of NAD + levels by PARP1 reduces SIRT1 activity and inhibits the capability of SIRT1 to deacetylate its targets respond to genotoxic stress . PARP1 has also been implicated in caspase-independent apoptosis, where its activation leads to apoptosis-inducing factor (AIF) release from the mitochondria, which induces nuclear chromatin fragmentation [[A59]] .

HGNC:270 = **PARP1**     
GO:GO:0008219 = **cell death**     
GO:GO:0006915 = **apoptotic process**     
GO:GO:0070265 = **None**     
MESH:D004249 = **DNA Damage**     
CHEBI:CHEBI:15422 = **ATP**     
FPLX:Caspase = **Caspase**     
CHEBI:CHEBI:15422 = **ATP**     
GO:GO:0006915 = **apoptotic process**     
HGNC:270 = **PARP1**     
FPLX:Caspase = **Caspase**     
HGNC:270 = **PARP1**     
CHEBI:CHEBI:13389 = **NAD**     
CHEBI:CHEBI:15422 = **ATP**     
HP:HP:0012828 = **Severe**     
MESH:D004249 = **DNA Damage**     
CHEBI:CHEBI:13389 = **NAD**     
GO:GO:0070265 = **None**     
CHEBI:CHEBI:15422 = **ATP**     
HP:HP:0012828 = **Severe**     
MESH:D004249 = **DNA Damage**     
GO:GO:0070265 = **None**     
CHEBI:CHEBI:34922 = **picloram**     
MESH:D007700 = **Kinetics**     
CHEBI:CHEBI:13389 = **NAD**     
HGNC:270 = **PARP1**     
CHEBI:CHEBI:13389 = **NAD**     
HGNC:270 = **PARP1**     
HGNC:14929 = **SIRT1**     
HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
GO:GO:0012501 = **programmed cell death**     
MESH:D051033 = **Apoptosis Inducing Factor**     
HGNC:8768 = **AIFM1**     
GO:GO:0005739 = **mitochondrion**     
GO:GO:0000785 = **chromatin**     

*PARP1 plays a role in cell death pathways (apoptosis or necrosis) in the course of responding to DNA damage.*
- `p(HGNC:PARP1) increases bp(GO:"cell death")`

*ATP is required for optimal caspase activation*
- `a(CHEBI:ATP) increases act(complex(FPLX:Caspase))`

*Cells with severe DNA damage die from necrosis because they are not able to switch away from the necrotic pathway*
- `bp(GO:"DNA damage") increases bp(GO:"cell death")`

*Rapid depletion of NAD+ levels by PARP1 reduces SIRT1 activity*
- `p(HGNC:PARP1) decreases a(CHEBI:NAD)`

*Rapid depletion of NAD+ levels by PARP1 reduces SIRT1 activity*
- `p(HGNC:PARP1) decreases act(p(HGNC:SIRT1))`

*PARP1 has been implicated in caspase-independent apoptosis*
- `p(HGNC:PARP1) increases bp(GO:"apoptotic process")`

*PARP1 activation leads to apoptosis-inducing factor (AIF) release from the mitochondria*
- `p(HGNC:PARP1) increases sec(p(MESH:"Apoptosis Inducing Factor"), fromLoc(GO:mitochondrion))`



## Paragraph 39

Recent SIRT1 and PARP1 research has uncovered roles for the two proteins in circadian rhythms creating the possibility for novel interconnections between metabolism, DNA repair, and circadian rhythms (Figure  6). The core circadian machinery involves a transactivating CLOCK/BMAL1 heterodimer, which induces the transcription of a large number of genes, including the cryptochrome (CRY1 and CRY2) and period (PER1, PER2, PER3) genes that form a complex that leads to a negative feedback loop suppressing CLOCK/BMAL1-mediated transcription [[A60-A62]]. Several studies have shown that disruptions in core circadian interactions can lead to alterations in DDR; reviewed in .

HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
MESH:D012106 = **Research**     
CHEBI:CHEBI:50906 = **role**     
GO:GO:0007623 = **circadian rhythm**     
GO:GO:0008152 = **metabolic process**     
GO:GO:0006281 = **DNA repair**     
GO:GO:0007623 = **circadian rhythm**     
GO:GO:0006351 = **DNA-templated transcription**     
HGNC:6511 = **LARGE1**     
MESH:D056931 = **Cryptochromes**     
HGNC:2384 = **CRY1**     
HGNC:2385 = **CRY2**     
HGNC:8845 = **PER1**     
HGNC:8846 = **PER2**     
HGNC:8847 = **PER3**     
MESH:D005246 = **Feedback**     
GO:GO:0006351 = **DNA-templated transcription**     
GO:GO:0042769 = **None**     

*The core circadian machinery involves a transactivating CLOCK/BMAL1 heterodimer, which induces the transcription of a large number of genes*
- `complex(p(HGNC:CLOCK), p(HGNC:LARGE1)) increases bp(GO:"DNA-templated transcription")`

*The core circadian machinery involves a transactivating CLOCK/BMAL1 heterodimer, which induces the transcription of a large number of genes, including the cryptochrome (CRY1 and CRY2)*
- `complex(p(HGNC:CLOCK), p(HGNC:LARGE1)) increases g(HGNC:CRY1)`

*The core circadian machinery involves a transactivating CLOCK/BMAL1 heterodimer, which induces the transcription of a large number of genes, including the cryptochrome (CRY1 and CRY2)*
- `complex(p(HGNC:CLOCK), p(HGNC:LARGE1)) increases g(HGNC:CRY2)`

*The core circadian machinery involves a transactivating CLOCK/BMAL1 heterodimer, which induces the transcription of a large number of genes, including the period (PER1, PER2, PER3) genes*
- `complex(p(HGNC:CLOCK), p(HGNC:LARGE1)) increases g(HGNC:PER1)`

*The core circadian machinery involves a transactivating CLOCK/BMAL1 heterodimer, which induces the transcription of a large number of genes, including the period (PER1, PER2, PER3) genes*
- `complex(p(HGNC:CLOCK), p(HGNC:LARGE1)) increases g(HGNC:PER2)`

*The core circadian machinery involves a transactivating CLOCK/BMAL1 heterodimer, which induces the transcription of a large number of genes, including the period (PER1, PER2, PER3) genes*
- `complex(p(HGNC:CLOCK), p(HGNC:LARGE1)) increases g(HGNC:PER3)`

*CRY and PER genes form a complex that leads to a negative feedback loop suppressing CLOCK/BMAL1-mediated transcription*
- `complex(p(HGNC:CRY1), p(HGNC:PER1), p(HGNC:PER2), p(HGNC:PER3)) decreases bp(GO:"DNA-templated transcription")`



## Paragraph 40

Interactions of SIRT1 and PARP1 with circadian clock components.

HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
MESH:D057906 = **Circadian Clocks**     

*Interactions of SIRT1 and PARP1 with circadian clock components.*
- `p(HGNC:SIRT1) regulates bp(MESH:"Circadian Clocks")`

*Interactions of SIRT1 and PARP1 with circadian clock components.*
- `p(HGNC:PARP1) regulates bp(MESH:"Circadian Clocks")`



## Paragraph 41

SIRT1 deacetylates BMAL1 at K537 destabilizing the interaction between CRY and BMAL1 [[A63]] . CLOCK possesses acetyltransferase activity that regulates the transcriptional activity of CLOCK/BMAL1  and is capable of acetylating some of the same locations that SIRT1 deacetylates: H3K9, H3K14, and BMAL1 at K537 [[A64]] . SIRT1 has also been shown to deacetylate PER2 destabilizing the protein [[A65]]; it has been hypothesized that acetylation of PER2 at lysine residues prevents their ubiquitination . This presents a dual control mechanism for SIRT1 in the circadian clock where it is capable of balancing transcription through chromatin condensation, but also by disrupting the ability for CRY and PER2 to repress CLOCK/BMAL1 activity. SIRT1 is involved in NAMPT transcriptional regulation, which is under circadian control causing NAD + levels to oscillate as a consequence of NAMPT level oscillation . Additionally, it has been shown that PARP1 has rhythmic activity influenced by feeding patterns though further work is necessary to understand the underlying molecular mechanism. PARP1 is capable of ADP-ribosylating CLOCK in a circadian manner disrupting the association between the BMAL1/CLOCK heterodimer and its targets [[A66]] . It remains to be determined whether a regulatory effect exists between SIRT1 or PARP1 and the circadian components during DNA damage.

HGNC:14929 = **SIRT1**     
HGNC:701 = **BMAL1**     
HGNC:18246 = **CRYL1**     
HGNC:701 = **BMAL1**     
HGNC:2082 = **CLOCK**     
GO:GO:0016407 = **acetyltransferase activity**     
HGNC:14929 = **SIRT1**     
HGNC:701 = **BMAL1**     
HGNC:14929 = **SIRT1**     
HGNC:8846 = **PER2**     
MESH:D000107 = **Acetylation**     
HGNC:8846 = **PER2**     
CHEBI:CHEBI:32568 = **lysine residue**     
MESH:D054875 = **Ubiquitination**     
HGNC:14929 = **SIRT1**     
MESH:D057906 = **Circadian Clocks**     
GO:GO:0006351 = **DNA-templated transcription**     
GO:GO:0000785 = **chromatin**     
HGNC:18246 = **CRYL1**     
HGNC:8846 = **PER2**     
HGNC:14929 = **SIRT1**     
HGNC:30092 = **NAMPT**     
CHEBI:CHEBI:13389 = **NAD**     
HGNC:30092 = **NAMPT**     
HGNC:270 = **PARP1**     
MESH:D014937 = **Work**     
HGNC:270 = **PARP1**     
HGNC:2082 = **CLOCK**     
MESH:D001244 = **Association**     
HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
MESH:D004249 = **DNA Damage**     

*SIRT1 deacetylates BMAL1 at K537 destabilizing the interaction between CRY and BMAL1*
- `p(HGNC:SIRT1, pmod(Ac)) directlyDecreases complex(p(HGNC:BMAL1), p(HGNC:CRYL1))`

*CLOCK possesses acetyltransferase activity that regulates the transcriptional activity of CLOCK/BMAL1*
- `p(HGNC:CLOCK) hasActivity ma(GO:0016407)`

*CLOCK possesses acetyltransferase activity that regulates the transcriptional activity of CLOCK/BMAL1*
- `p(HGNC:CLOCK) increases act(complex(p(HGNC:CLOCK), p(HGNC:BMAL1)))`

*SIRT1 has also been shown to deacetylate PER2 destabilizing the protein*
- `p(HGNC:SIRT1, pmod(Ac)) directlyDecreases p(HGNC:PER2)`

*PARP1 is capable of ADP-ribosylating CLOCK in a circadian manner disrupting the association between the BMAL1/CLOCK heterodimer and its targets*
- `p(HGNC:PARP1) decreases complex(p(HGNC:BMAL1), p(HGNC:CLOCK))`



## Paragraph 42

Interactions with other family members

MESH:D005190 = **Family**     



## Paragraph 43

While the focus of this review has been on the inter-relationships that exist between SIRT1 and PARP1, there is growing evidence that SIRT1 has the capability of interacting with other members of the PARP family of proteins and similarly that PARP1 is capable of interacting with multiple sirtuins. Here we present three cases of these interactions; these interactions range include both direct modifications, as well as transcriptional regulation. First, SIRT6, one of the nuclear sirtuins, plays a role in promoting DNA damage repair by binding and activating PARP1 by mono-ADP-ribosylating PARP1 triggering its auto-ADP-ribosylation activity [[A67]] . Next, the second PARP family member, PARP2, has been shown to inhibit the transcription of SIRT1; the deletion of PARP2 increases overall levels of SIRT1 activity without having to target NAD + levels directly [[A68]] . This finding indicates that inhibitors of PARP proteins may be capable of increasing SIRT1 activity not only via the inhibition of NAD + consumption by PARP family members, but also through the removal of transcriptional inhibition. Lastly, shown recently is that PARP1 increases levels of mitochondrial SIRT3 and that SIRT3 can continue to function under stress conditions because mitochondrial NAD + levels are maintained in the conditions produced by either treatment with methylnitronitrosoguanidine (MNNG), a carcinogen, or N-methyl-D-aspartate (NMDA), a neuronal stressor, even as cytosolic levels of NAD + are depleted by PARP1 . This study by Kim et al., did not observe a similar change in SIRT1 protein levels or the expression levels of the other mitochondrial sirtuins, SIRT4 and SIRT5.

MESH:D016454 = **Review**     
HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
MESH:D005190 = **Family**     
HGNC:270 = **PARP1**     
MESH:D037761 = **Sirtuins**     
HGNC:14934 = **SIRT6**     
MESH:D037761 = **Sirtuins**     
MESH:D004249 = **DNA Damage**     
HGNC:270 = **PARP1**     
HGNC:270 = **PARP1**     
HGNC:270 = **PARP1**     
MESH:D005190 = **Family**     
HGNC:272 = **PARP2**     
GO:GO:0006351 = **DNA-templated transcription**     
HGNC:14929 = **SIRT1**     
EFO:0004014 = **deletion**     
HGNC:272 = **PARP2**     
MESH:D016424 = **Overall**     
HGNC:14929 = **SIRT1**     
CHEBI:CHEBI:13389 = **NAD**     
MESH:D012816 = **Signs and Symptoms**     
CHEBI:CHEBI:35222 = **inhibitor**     
HGNC:270 = **PARP1**     
HGNC:14929 = **SIRT1**     
CHEBI:CHEBI:13389 = **NAD**     
HGNC:270 = **PARP1**     
MESH:D005190 = **Family**     
HGNC:270 = **PARP1**     
HGNC:14931 = **SIRT3**     
HGNC:14931 = **SIRT3**     
CHEBI:CHEBI:13389 = **NAD**     
CHEBI:CHEBI:21759 = **N-methyl-N'-nitro-N-nitrosoguanidine**     
CHEBI:CHEBI:21759 = **N-methyl-N'-nitro-N-nitrosoguanidine**     
CHEBI:CHEBI:50903 = **carcinogenic agent**     
CHEBI:CHEBI:31882 = **N-methyl-D-aspartic acid**     
CHEBI:CHEBI:31882 = **N-methyl-D-aspartic acid**     
CHEBI:CHEBI:13389 = **NAD**     
HGNC:270 = **PARP1**     
HGNC:14929 = **SIRT1**     
MESH:D037761 = **Sirtuins**     
HGNC:14932 = **SIRT4**     
HGNC:14933 = **SIRT5**     

*SIRT6, one of the nuclear sirtuins, plays a role in promoting DNA damage repair by binding and activating PARP1 by mono-ADP-ribosylating PARP1 triggering its auto-ADP-ribosylation activity*
- `p(HGNC:SIRT6) increases act(p(HGNC:PARP1))`

*PARP2 has been shown to inhibit the transcription of SIRT1; the deletion of PARP2 increases overall levels of SIRT1 activity without having to target NAD+ levels directly*
- `p(HGNC:PARP2) decreases r(HGNC:SIRT1)`

*PARP1 increases levels of mitochondrial SIRT3 and that SIRT3 can continue to function under stress conditions because mitochondrial NAD+ levels are maintained*
- `p(HGNC:PARP1) increases p(HGNC:SIRT3)`



## Paragraph 44

Cells respond to DNA damage through coordinated pathways that arrest the cell cycle and repair the damage, and in the presence of severe damage trigger cell death. Both SIRT1 and PARP1 play an intimate role in the regulation of genomic stability, and continued work is necessary for the understanding of the specific contexts in which modulators of SIRT1 and PARP1 activity may be appropriate as therapeutics for cancer and metabolic disorders. The regulation of SIRT1 and PARP1 is controlled by a variety of stimuli, including metabolic, circadian, and genotoxic. Understanding how each of these stimuli affects the regulatory network of these two proteins is vital.

MESH:D004249 = **DNA Damage**     
HP:HP:0012828 = **Severe**     
GO:GO:0008219 = **cell death**     
HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
MESH:D014937 = **Work**     
MESH:D032882 = **Comprehension**     
HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
MESH:D013812 = **Therapeutics**     
MESH:D009369 = **Neoplasms**     
MESH:D008659 = **Metabolic Diseases**     
HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
EFO:0001461 = **control**     
MESH:D032882 = **Comprehension**     
MESH:D000339 = **Affect**     

*Cells respond to DNA damage through coordinated pathways that arrest the cell cycle and repair the damage, and in the presence of severe damage trigger cell death.*
- `bp(MESH:"DNA Damage") increases bp(GO:"cell death")`

*Both SIRT1 and PARP1 play an intimate role in the regulation of genomic stability*
- `p(HGNC:SIRT1) regulates bp(MESH:"DNA Damage")`

*Both SIRT1 and PARP1 play an intimate role in the regulation of genomic stability*
- `p(HGNC:PARP1) regulates bp(MESH:"DNA Damage")`

*continued work is necessary for the understanding of the specific contexts in which modulators of SIRT1 and PARP1 activity may be appropriate as therapeutics for cancer and metabolic disorders*
- `composite(p(HGNC:SIRT1), p(HGNC:PARP1)) regulates path(MESH:Neoplasms)`

*continued work is necessary for the understanding of the specific contexts in which modulators of SIRT1 and PARP1 activity may be appropriate as therapeutics for cancer and metabolic disorders*
- `composite(p(HGNC:SIRT1), p(HGNC:PARP1)) regulates path(MESH:"Metabolic Diseases")`



## Paragraph 45

The work of the past several years has trended towards an understanding of the diverse regulatory network surrounding these two proteins, the effects of local levels of their common substrate, NAD+, and the co-regulation of and by the two proteins. There continue to be several unexplored areas. For example, understanding the nature of competitive regulation of acetylation and PAR at a single substrate residue on a single molecule, since both can target lysine residues, remains an open area of research. Another interesting avenue of research remaining to be thoroughly explored is the alteration of the reviewed pathways as an organism ages. Studies have shown age-dependent increases in DNA damage can lead to NAD + depletion . In human tissue samples, Massudi et al. found an age-related positive correlation in PARP1 activity in males and negative correlations with SIRT1 activity in males and NAD + levels in both males and females that starts to shed light on the role of these two proteins in the presence of accumulating DNA damage with age . In a related study, Chang et al. showed a reduction in SIRT1 levels over time resulting in alterations in circadian oscillations in mice as they age . Studies such as these suggest that the regulatory network surrounding SIRT1 and PARP1 may undergo large-scale changes over an organism's lifespan; currently, we do not know the extent of these changes. Additionally, there is a deficit in our knowledge with respect to the influence that DNA damage response may have on circadian regulation and vice versa and the roles that SIRT1 and PARP1 may play. And while this review has focused on evidence of the interactions between the better studied members of their respective protein families, SIRT1 and PARP1, additional work is necessary in our understanding of the roles of the other members of the two protein families and their unique properties and interactions that may play integral roles in the progression of DDR, as well as other processes.

MESH:D014937 = **Work**     
HGNC:3242 = **EHD1**     
MESH:D032882 = **Comprehension**     
EFO:0005061 = **substrate**     
CHEBI:CHEBI:15846 = **NAD(+)**     
MESH:D032882 = **Comprehension**     
MESH:D019368 = **Nature**     
MESH:D000107 = **Acetylation**     
HGNC:6201 = **JTB**     
EFO:0005061 = **substrate**     
CHEBI:CHEBI:25367 = **molecule**     
CHEBI:CHEBI:32568 = **lysine residue**     
MESH:D012106 = **Research**     
MESH:D012106 = **Research**     
EFO:0000246 = **age**     
MESH:D004249 = **DNA Damage**     
CHEBI:CHEBI:13389 = **NAD**     
MESH:D006801 = **Humans**     
CHEBI:CHEBI:28984 = **aluminium atom**     
HGNC:270 = **PARP1**     
MESH:D008297 = **Male**     
HGNC:14929 = **SIRT1**     
MESH:D008297 = **Male**     
CHEBI:CHEBI:13389 = **NAD**     
MESH:D008297 = **Male**     
MESH:D005260 = **Female**     
MESH:D004249 = **DNA Damage**     
CHEBI:CHEBI:28984 = **aluminium atom**     
HGNC:14929 = **SIRT1**     
HGNC:7094 = **MICE**     
HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
MESH:D019359 = **Knowledge**     
MESH:D000078682 = **Respect**     
GO:GO:0006974 = **DNA damage response**     
CHEBI:CHEBI:50906 = **role**     
HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
MESH:D016454 = **Review**     
MESH:D005190 = **Family**     
HGNC:14929 = **SIRT1**     
HGNC:270 = **PARP1**     
MESH:D014937 = **Work**     
MESH:D032882 = **Comprehension**     
CHEBI:CHEBI:50906 = **role**     
MESH:D005190 = **Family**     
CHEBI:CHEBI:50906 = **role**     
GO:GO:0042769 = **None**     

*Studies have shown age-dependent increases in DNA damage can lead to NAD + depletion*
- `bp(GO:"DNA damage response") negativeCorrelation p(HGNC:SIRT1)`

*Studies have shown age-dependent increases in DNA damage can lead to NAD + depletion*
- `bp(GO:"DNA damage response") decreases a(CHEBI:"NAD(+)")`

*In human tissue samples, Massudi et al. found an age-related positive correlation in PARP1 activity in males*
- `bp(GO:"DNA damage response") positiveCorrelation p(HGNC:PARP1)`

*In human tissue samples, Massudi et al. found negative correlations with SIRT1 activity in males*
- `bp(GO:"DNA damage response") negativeCorrelation p(HGNC:SIRT1)`

*In human tissue samples, Massudi et al. found negative correlations with NAD + levels in both males and females*
- `bp(GO:"DNA damage response") decreases a(CHEBI:"NAD(+)")`

*Chang et al. showed a reduction in SIRT1 levels over time resulting in alterations in circadian oscillations in mice as they age*
- `p(HGNC:SIRT1) regulates bp(GO:"circadian rhythm")`



## Paragraph 46

The authors declare that they have no competing interests.




## Paragraph 47

Authors' contributions




## Paragraph 48

AL wrote the manuscript and drew and annotated the supplemental MIM. MIA and KWK edited the manuscript and MIM. All authors have read and approved the final manuscript.

EFO:0005318 = **axial length measurement**     
MESH:D020486 = **Manuscript**     
HGNC:20443 = **MTSS1**     
HGNC:7076 = **MIA**     
MESH:D020486 = **Manuscript**     
HGNC:20443 = **MTSS1**     
DOID:DOID:1996 = **rectum adenocarcinoma**     
MESH:D020486 = **Manuscript**     

*AL wrote the manuscript and drew and annotated the supplemental MIM.*
- `p(HGNC:MTSS1) hasActivity bp(EFO:'axial length measurement')`

*MIA and KWK edited the manuscript and MIM.*
- `p(HGNC:MIA) hasActivity bp(MESH:Manuscript)`



## Paragraph 49

Supplementary Material

MESH:D058537 = **Electronic Supplementary Materials**     



## Paragraph 50

We would like to acknowledge helpful discussions with Paolo Sassone-Corsi and Myriam Gorospe. This project was supported by the Ford Foundation and the Intramural Research Program of the NIH, Center for Cancer Research, National Cancer Institute.

MESH:D005582 = **Foundations**     
MESH:D012106 = **Research**     
MESH:D019542 = **Program**     
MESH:D009369 = **Neoplasms**     
MESH:D012106 = **Research**     
MESH:D054547 = **National Cancer Institute (U.S.)**     

*This project was supported by the Ford Foundation and the Intramural Research Program of the NIH, Center for Cancer Research, National Cancer Institute.*
- `path(MESHD:Neoplasms) supports bp(MESHD:Research)`


