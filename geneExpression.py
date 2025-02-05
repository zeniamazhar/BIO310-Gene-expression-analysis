# -*- coding: utf-8 -*-
"""
The modules we are going to use are as followed:
1. PyDESeq2: is for Differential gene expression analysis. It is Python implementation of DESeq2 library which is originally in R.
2. GSEApy: is a Python/Rust implementation of GSEA and wrapper for Enrichr. Enrichr contains most comprehensive and popular gene set libraries. We are going to use it for gene set enrichment over the selected libraries to see which biological pathways are enriched on up-regulated and down-regulated gene sets.
"""

# After installing the below modules, dont forget to restart the runtime, as it needs to change the modules which the versions are changed.
!pip install --quiet numpy==1.23.0 pydeseq2 gseapy dash-bio

# This error is not a problem for our tasks:
# ERROR: pip's dependency resolver does not currently take into account all the packages that are installed.

"""After restarting the runtime, Import the following modules. If you dont restart, numpy will give an error.


"""

import pandas as pd
import numpy as np
import copy
np.seterr(all="ignore")

# DGE and Pathway Enrichment
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats
import gseapy as gp
from gseapy import Biomart

# PCA
from sklearn.decomposition import PCA

# Viz.
import plotly.express as px
import dash_bio
from gseapy import dotplot

"""The following are helper functions for visualizations that are in DESeq2 but not in PyDESeq2 such as: Run PCA/plot, Volcano Plot, Dispersion Plot, MA Plot.

Run the following cell as we are going to need these functions in the downstream analysis.
"""

def plotPCA(dds, clinical_df, nTop=0, vst=True, returnData=False):

  if vst:
    counts = dds.layers['vst_counts']
  else:
    counts = dds.layers['normed_counts']

  colwise_var = np.var(counts, axis=0)
  idx = np.argpartition(colwise_var, -nTop)[-nTop:] if nTop > 0 else (-colwise_var).argsort()[:]

  pca = PCA(n_components=3)
  pca_data = pca.fit_transform(counts[:, idx])
  print(f'Explained Variance Ratio :{sum(pca.explained_variance_ratio_)}')

  index_to_use = dds.obsm['design_matrix'].index
  pca_df = pd.DataFrame(
      {'pc1': pca_data[:,0],
       'pc2': pca_data[:,1],
       'pc3': pca_data[:,2],
       'organ': clinical_df.loc[index_to_use]['organ'],
       'condition': clinical_df.loc[index_to_use]['condition']})

  fig = px.scatter_3d(pca_df, x='pc1', y='pc2', z='pc3',
                    color='organ', symbol='condition')
  fig.show()

  if returnData:
    return pca, pca_data

def plotVolcano(stat_res, lfc_thr=[-1, 1], padj_thr=0.05):
  res_df = stat_res.results_df

  plot_df = res_df.dropna()
  plot_df = pd.DataFrame({
      'EFFECTSIZE': np.array(plot_df['log2FoldChange']).astype(float),
      'P': np.array(plot_df['padj']).astype(float),
      'GENE': list(plot_df.index)})

  fig = dash_bio.VolcanoPlot(
      dataframe=plot_df,
      snp=None,
      genomewideline_value=-np.log10(padj_thr),
      effect_size_line=lfc_thr,
      ylabel='-log10(Adjusted p-value)',
      xlabel='Effect Size: log2(fold-change)')

  fig.show()

def plotDispEsts(dds):
  gene_est = list(np.log(dds.varm['genewise_dispersions']))
  fit = list(np.log(dds.varm['fitted_dispersions']))
  final = list(np.log(dds.varm['dispersions']))
  n = len(gene_est)

  m_norm_counts = list(np.log(np.average(dds.layers['normed_counts'], axis=0)))

  plot_df = pd.DataFrame({
      'dispersion': gene_est + fit + final,
      'name': ['Genewise Dispersions'] * n + ['Fitted Dispersions'] * n + ['Final Dispersions'] * n,
      'mean_norm_counts': m_norm_counts * 3
  })

  fig = px.scatter(plot_df, y = 'dispersion', x = 'mean_norm_counts', color = 'name', opacity=0.8)
  fig.show()

def plotMA(stat_res, padj_thr=0.05):
  dds = stat_res.dds
  res_df = stat_res.results_df

  colors = ['sig' if float(padj) <= padj_thr else 'non-sig' for padj in list(res_df['padj'])]
  l2fc =list(res_df['log2FoldChange'])

  m_norm_counts = np.log10(np.average(dds.layers['normed_counts'], axis=0))

  plot_df = pd.DataFrame({
      'padj Significance': colors,
      'log2 Fold-Change': l2fc,
      'log10 (Mean of Normalized Counts Per Gene)': m_norm_counts
  })

  fig = px.scatter(plot_df, y = 'log2 Fold-Change', x = 'log10 (Mean of Normalized Counts Per Gene)', color = 'padj Significance')
  fig.show()

"""Download the dge-data.zip file from SUCourse and extract. You will find two text files. Upload them on this colab notebook. Run the below cell.

**Task 1**: Print the two dataframes that you have imported. What do you see, describe both of the dataframes.
"""

clinical_df = pd.read_csv('clinical.tsv', sep='\t')
clinical_df = clinical_df.set_index('sampleID')
clinical_df = clinical_df.sort_index(ascending=True)

counts_df = pd.read_csv('counts.tsv', sep='\t')
counts_df = counts_df.set_index('geneIDs')
counts_df = counts_df.T.loc[clinical_df.index]
counts_df = counts_df.sort_index(ascending=True)

# PRINT CLINICAL DF

print(clinical_df)

# PRINT COUNTS DF

print(counts_df)



"""<< The clinical_df shows the true labels of each of the samples with the sample ids and the labels, which include the organ names and the condition (untrt = untreated and cis=cisplatin-treated). The counts_df shows the gene expression levels observed in the experiments with all of the samples for each of the different genes, which have different ids listed in the gene_ids row.>>

**Task 2**: Keep only the columns in the counts_df that the sum of the counts are bigger or equal than 10 for each gene. We want to eliminate genes which produced very low counts across all samples.
"""

#Filter out genes that have less than 10 counts across samples

counts_df = counts_df.loc[:, counts_df.iloc[:, :].sum() >= 10]
counts_df

"""**Task 3**: You are going to create DeseqDataSet object from your counts_df and clinical_df. DeseqDataSet object contains the methods for DESeq2 workflow and necessary transformations.

Go to this [link](https://pydeseq2.readthedocs.io/en/latest/auto_examples/plot_minimal_pydeseq2_pipeline.html#sphx-glr-auto-examples-plot-minimal-pydeseq2-pipeline-py)

Try to understand how to create DeseqDataSet object.
"""

# Run this cell to create DESeq Dataset object as dds_all
dds_all = DeseqDataSet(
    counts=counts_df,
    metadata=clinical_df,
    design_factors="condition",
    refit_cooks=True,
)

# run the deseq2 workflow
dds_all.deseq2()

"""**Task 4**: DeseqDataSet object contains a method for Variance Stabilizing Transformation (use vst() method with default parameters). Apply it to dds_all. We need this method to transform normalized counts, so that we can perform a better PCA.

Hint: [Check how to with the docs](https://pydeseq2.readthedocs.io/en/latest/api/docstrings/pydeseq2.dds.DeseqDataSet.html#pydeseq2.dds.DeseqDataSet.vst)
"""

# Transform the normalized counts by Variance Stabilizing Transformation (vst) for PCA

dds_all.vst()

# and also run here, you should see 'vst_counts' in "layers"
dds_all

"""**Task 5**: Run the following cell to perform PCA and plot the results. Interpret the results with respect to biological relevance. (Such as in the contrast of different organs and treatment presence etc.)"""

plotPCA(dds_all, clinical_df, nTop=500, returnData=False)

"""<< There are 3 major clusters that have formed, 1 for the lung (shown in green), 1 for the liver (shown in red) and one for the kidney (shown in blue). These were 2 replicates used for each of the conditions (cis, representing the mouse organs treated with cisplatin, and untrt which represents the untreated population). This shows that these 3 cell types show differential gene expression when compared to each other, but the treated and untreated versions of each of the organs are still close enough in gene expression so that they can be clustered together. It seems that the within-group variability for the kidney cells is low, since the points seem closer together than in the case of lung and liver. When it comes to the separation between the treated and untreated samples, there isn't a clear pattern, since the treated samples are far away from each other in the liver and the lung, and there isn't a clear separation between the untreated and treated cells of any of the organ types that can be seen, except for the fact that the untreated samples lie lower on the graph than the treated samples when it comes to the kidney and lung cells. >>

**Task 6**: We want to perform differential expression analysis to understand the effects of cisplatin treatment on kidney. Filter the clinical_df, where you only keep the rows that the organ is kidney. Filter the counts_df accordingly. Create a new DeseqDataset object with new filtered data, and assign it to dds.

Dont forget to use **ref_level** parameter this time (It is a parameter in DeseqDataSet function). Because we want our base level to be untreated samples. So that, positive fold changes of expression will be the genes that are upregulated after cisplatin treatment, and negative fold changes of expression will be the genes that are downregulated after cisplatin treatment.

Hint: Be careful with the DataFrame indexes. They should match between counts and metadata.

Hint2: [Check how to with the docs](https://pydeseq2.readthedocs.io/en/latest/api/docstrings/pydeseq2.dds.DeseqDataSet.html#pydeseq2.dds.DeseqDataSet)
"""

df_kidney_clinical = clinical_df[clinical_df.iloc[:,0]== 'kidney'] ##df[df['hi'] == specific_value]

df_kidney_counts = counts_df.loc[['GSM3272779','GSM3272780' ,'GSM3272781' , 'GSM3272782']]


dds = DeseqDataSet(
    counts=df_kidney_counts,
    metadata=df_kidney_clinical,
    design_factors="condition",
    refit_cooks=True,
    ref_level=["condition","untrt"],
)





# Run DESeq2 workflow to Perform dispersion and log fold-change (LFC) estimation.
dds.deseq2()

"""**Task7**: Go to the [link](https://hbctraining.github.io/DGE_workshop/lessons/04_DGE_DESeq2_analysis.html). Do not try to use the code in the link -on here- because it is for original implementation of DESeq2 in R. Try to understand how DESeq2 controls dispersion. Run the following cell to plot dispersion plot. Do you think the data is a good fit for the DESeq2 model? Explain what you see."""

# Plot dispersions
plotDispEsts(dds)

"""<< According to the website provided, the dispersion is inversely proportional to the mean counts, and this is true to a good extent here, since majority of the samples fit the model in the graph. But, there are many samples that have small dispersion (of around 18.42) which have varying mean_norm_counts. Also, the negative slope isn't very steep, which may be another indicator that the data actually doesn't fit this model well. >>"""

# # Run this cell for the statistical tests for differential expression and lfc shrink
stat_res = DeseqStats(dds)
stat_res.summary()
stat_res_unshrunken = copy.deepcopy(stat_res)
# Shrink lfc
stat_res.lfc_shrink(coeff="condition_cis_vs_untrt")

"""**Task8**: Go to this [link](https://hbctraining.github.io/DGE_workshop/lessons/05_DGE_DESeq2_analysis2.html) Try to understand statistical analysis that is performed by DESeq2 and how log2 foldchange shrinkage is applied. Next, Plot MA plot for shrunken lfc and unshrunken lfc. What do you see different?

Do not try to use the code in the link -on here- because it is for original implementation of DESeq2 in R.
"""

#MA Plot for shrunken lfc
plotMA(stat_res, padj_thr=0.05)

#MA Plot for unshrunken lfc
plotMA(stat_res_unshrunken, padj_thr=0.05)

"""<< The two graphs are very different: the unshrunken version includes noisy data, hence the data is more dispersed, and this is especially true for the low mean of normalized counts as can be seen in the plot (this means that at lower levels of differential expression, there is higher variance in the lfc) - while the shrunken version, where the noisy measurements have been removed and the estimates are closer to 0, the data is more uniform and less dispersed.>>

Volcano plot is a great way to get an overall picture of what is going on, where we plot the log transformed adjusted p-values plotted on the y-axis and log2 fold change values on the x-axis.
"""

#Volcano Plot
plotVolcano(stat_res)

"""Inspect the results table (res_df) that is created after statistical tests."""

res_df = stat_res.results_df
res_df

"""**Task9:**

What does fold change mean? Where is p-value coming from? What is padj (Adjusted p-value)? What is Multiple test correction? Check again the link in Task8.

Filter the res_df where padj is smaller or equal to .05. So that we get differentially expressed genes that statistically significant.

Then,

Filter the res_df where log2FoldChange is bigger or equal than 1, and assign it to up_degs. (Up regulated genes where fold change is 2 times changed, log2foldchange 1 means 2)

Filter the res_df where log2FoldChange is smaller or equal than -1, and assign it to down_degs. (Down regulated genes where fold change is halfed, log2foldchange -1 means .5)

<< The fold change shows the differenential expression ratio between 2 conditions (in this case, the treated vs. the untreated condition). The p-value is coming from the Wald test. The adjusted p-value comes from using the Benjamini-Hochberg method, where each gene is ranked by the p-value and each p-value is multiplied by (the total number of tests/rank). Multiple test correction is needed whenever there are many tests being performed because if we take the p-value and use some cut-off value (i.e: 0.05), there would be a cumulative effect where each of the tests would have a small chance of having false positives which would add up to be a big value at the end (i.e: if we have 10 tests and we use 0.05 as our cut-off value, it results in 10*0.05 = 0.5 false positives, which means theres a 50% chance of getting false positives), so we use multiple test correction to pick the true positives.>>
"""

# filter the res_df based on log2FC and Adjusted p-value as described above
res_df = res_df[res_df['padj']<=0.05]
up_degs_df = res_df[res_df['log2FoldChange']>=1]
down_degs_df = res_df[res_df['log2FoldChange']<=-1]

"""After obtaining gene sets (dataframes) of upregulated and downregulated genes, we will perform gene set enrichment, with EnrichR api inside GSEApy. EnrichR needs Entrez Gene names instead of Ensembl gene ids. Think of it as different databases name genes differently.

Run the following cell.
"""

# Convert ensembl gene ids to Entrez Gene Names using biomart api inside gseapy via batch submission

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def batch_subs(degs, n=200):
  bm = Biomart()

  gene_names = []
  for batch in chunks(degs, n):

    queries ={'ensembl_gene_id': batch }
    results = bm.query(dataset='mmusculus_gene_ensembl',
                      attributes=['entrezgene_accession'],
                      filters=queries)
    gene_names += list(results['entrezgene_accession'])

  return [i.upper() for i in gene_names]

gene_names_up = batch_subs(up_degs_df.index)
gene_names_down = batch_subs(down_degs_df.index)

"""Also run the following cell to briefly inspect the API returns of Entrez gene names for corresponding gene ids for the first 5 of them, and the total length of the corresponding lists."""

gene_names_up[:5], len(set(gene_names_up)), gene_names_down[:5], len(set(gene_names_down))

"""**Task10**: Run the following cell. You will see all of the Mouse gene set libraries that are present within EnrichR. You will see a lot of GO and KEGG database names with different years of version. What is [GO](http://geneontology.org/) database? GO is spllited into 3 major ontologies; Molecular Function, Cellular Component, Biological Process, what are they and how are they different? What is [KEGG](https://www.genome.jp/kegg/pathway.html) pathway database?"""

# Check out libraries that are present for Mouse
gp.get_library_name(organism='Mouse')

"""<< The GO database has annotated genes (with 'GO terms') that represent the products and the function of the gene. The factors used to make the GO terms are Molecular Function, Cellular Component, Biological Process. Molecular function refers to the role of the gene in the cell. The activities performed by the gene products are represented by this. The cellular component is the location of the gene - this can be (1) the "cellular anatomical entities" which includes the cellular structures where the function of the gene products is carried out, and (2) the macromolecular complexes the gene products are a part of. Lastly, the Biological Process refers to the big processes the gene products are a part of, where multiple molecular activities work together to finish the process (it is to be noted that this isn't a pathway, but rather the process the gene products are a part of). The KEGG pathway database is a collection of pathways, each of which are represented by a 2-4 letter prefix code and 5-digit number.>>

Run the following 4 cells, where we are going to use library of **GO_Biological_Process_2021** with our **Over-representation analysis.**
"""

# Up-regulated genes, cis vs untrt
enr_up = gp.enrichr(gene_list=gene_names_up,
                 gene_sets=['GO_Biological_Process_2021'],
                 organism='mouse',
                 outdir=None,
                )
enr_res_up = enr_up.results

enr_res_up.loc[enr_res_up['Adjusted P-value'] < .05]

dotplot(enr_up.res2d, title='UP Genes - GO_Biological_Process_2021',cmap='viridis_r', size=10, figsize=(3,5))

# Down-regulated genes, cis vs untrt
enr_down = gp.enrichr(gene_list=gene_names_down,
                 gene_sets=['GO_Biological_Process_2021'],
                 organism='mouse',
                 outdir=None,
                )
enr_res_down = enr_down.results

enr_res_down.loc[enr_res_down['Adjusted P-value'] < .05]

dotplot(enr_down.res2d, title='DOWN Genes - GO_Biological_Process_2021',cmap='viridis_r', size=10, figsize=(3,5))

"""**Task11:** You have printed the dataframes of signigicant pathways that are enriched in down- and up-regulated genes, seperately. You have also drawn the dotplots of the major pathways associated with them, coming from the respective dataframes.

Inspect the both results while considering biological relevance to cisplatin treatment. What do you think cisplatin caused?

<<Most of the upregulated genes seem to be related to misfolded proteins and apoptosis/cell death. The "regulation of cellular response to stress" get upregulated, which is a kind of defense mechanism that occurs when the protein folding ability of the endoplasmic reticulum (ER) is disturbed somehow, in order to restore the function of the ER. Moreover, mutations in the E3 ubiquitin ligase are what cause the ER stress to occur, which is supported by there being an upregulation of the genes related to "regulation of cellular response to stress" as well as the "regulation of protein ubiquitination", which involves enzymes, including E3s according to a paper titled "Ubiquitination in the regulation of inflammatory cell death and cancer" (Cockram et al., 2021). ER stress can also be caused when there are too many newly synthesized proteins that need to be folded (Haeri and Knox, 2021), which is also supported by the fact there is an increase in the genes responsible for the "negative regulation of transcription by RNA polymerase II". Overall, this shows that cisplatin may be causing mutations in the part of the DNA encoding the E3 ubiquitin ligase enzyme, which results in ER stress, which then leads to apoptosis/cell death. Most of the downregulated genes are related to transcription, signal transduction and migration. The downregulation of the filopodium assembly genes shows that the filopodium which is responsible for migration has been stopped from being assembled - this is something that cancer cells in malignant tumors do which is what makes the cancer so dangerous, hence it is possible that the cisplatin is responsible for this, or perhaps this is just related to the apoptotic genes being upregulated, which then causes these genes to be downregulated so that the cell can be killed. The upregulation of the apoptotic genes may be the reason why the genes responsible for the positive developmental process got downregulated. The downregulation of the genes responsible for the transcription initiation from RNA polymerase II. RNA polymerase II is responsible for transcribing DNA to RNA, which is halted, possibly because cell death is about to occur.

Overall, the big picture may be that the ER-stress induced apoptosis is occurring in the cells treated with cisplatin. >>
"""
