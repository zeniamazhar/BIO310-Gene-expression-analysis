# 🧬 Gene Expression Analysis
In this bioinformatics assignment, I had to use Principle Component Analysis (PCA) to visualize the similarities and differences between the samples based on their gene expression profiles. It was a useful way to check if the samples clustered together based on the expected biological variables (e.g., organ type or treatment condition).

Next, I had to compare gene expression in different conditions (different organs or treatment conditions). To do this, I used a statistical method called differential gene expression analysis. This method compares the expression of each gene between two or more conditions and identified genes that were expressed differently. I used DESeq2 to perform differential gene expression analysis.

Finally, the differentially expressed genes were identified in order to understand which biological pathways or processes were affected. This was done using gene set enrichment analysis, which compared the differentially expressed genes to known sets of genes involved in specific biological pathways or processes. I used GSEA to perform gene set enrichment analysis.

## The Data

Sequencing libraries created from total extracted mRNAs from different organs of healthy mice, after Cisplatin treatment or kept untreated.
For more info about the data: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE117167

## Aim
Cisplatin is a chemotherapy drug commonly used to treat various types of cancer. It works by binding to DNA molecules in cancer cells and causing damage to the DNA strands. The damage caused by cisplatin can activate the cell's DNA repair mechanisms, including nucleotide excision repair (NER).

Nucleotide excision repair is a DNA repair mechanism that removes and replaces damaged nucleotides (the building blocks of DNA) in the DNA strand. NER is a multi-step process that involves the recognition and removal of damaged DNA, followed by the insertion of new nucleotides to repair the damage.

In the case of cisplatin treatment, the drug causes a specific type of DNA damage known as DNA crosslinking, where the two strands of DNA are covalently linked together. This type of DNA damage is particularly toxic and can lead to cell death if left unrepaired. NER plays a critical role in repairing this type of damage caused by cisplatin.

However, cancer cells can also develop resistance to cisplatin by altering their DNA repair mechanisms, including NER. Some cancer cells may overexpress certain proteins involved in NER, allowing them to repair the DNA damage caused by cisplatin more efficiently and survive the treatment.

Overall, the relationship between cisplatin and NER is complex and can have significant implications for the effectiveness of cisplatin chemotherapy in treating cancer. Understanding this relationship is important for developing new strategies to overcome cisplatin resistance and improve cancer treatment outcomes.

This analysis aims to understand the difference in gene expression in mice when under cisplatin treatment vs. not under cisplatin treatment.

## Conclusion

As compared to the mice that were in the control group, the mice that were treated with cisplatin showed the following patterns: most of the upregulated genes seem to be related to misfolded proteins and apoptosis/cell death. The "regulation of cellular response to stress" get upregulated, which is a kind of defense mechanism that occurs when the protein folding ability of the endoplasmic reticulum (ER) is disturbed somehow, in order to restore the function of the ER. Moreover, mutations in the E3 ubiquitin ligase are what cause the ER stress to occur, which is supported by there being an upregulation of the genes related to "regulation of cellular response to stress" as well as the "regulation of protein ubiquitination", which involves enzymes, including E3s according to a paper titled "Ubiquitination in the regulation of inflammatory cell death and cancer" (Cockram et al., 2021). ER stress can also be caused when there are too many newly synthesized proteins that need to be folded (Haeri and Knox, 2021), which is also supported by the fact there is an increase in the genes responsible for the "negative regulation of transcription by RNA polymerase II". Overall, this shows that cisplatin may be causing mutations in the part of the DNA encoding the E3 ubiquitin ligase enzyme, which results in ER stress, which then leads to apoptosis/cell death. Most of the downregulated genes are related to transcription, signal transduction and migration. The downregulation of the filopodium assembly genes shows that the filopodium which is responsible for migration has been stopped from being assembled - this is something that cancer cells in malignant tumors do which is what makes the cancer so dangerous, hence it is possible that the cisplatin is responsible for this, or perhaps this is just related to the apoptotic genes being upregulated, which then causes these genes to be downregulated so that the cell can be killed. The upregulation of the apoptotic genes may be the reason why the genes responsible for the positive developmental process got downregulated. The downregulation of the genes responsible for the transcription initiation from RNA polymerase II. RNA polymerase II is responsible for transcribing DNA to RNA, which is halted, possibly because cell death is about to occur.

