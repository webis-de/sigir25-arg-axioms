
arg_translate_dict_tmp = {
    'QSenSim_max_exact_sbert': 'QSenSim$_{max}^{e}$',
    'QSenSim_max_sbert' : 'QSenSim$_{max}$',

    'QSenSim_mean_exact_sbert' : 'QSenSim$_{mean}^{e}$',
    'QSenSim_mean_sbert' : 'QSenSim$_{mean}$',

    #'QArgSim_max_exact_sbert': 'QArgSim$_{max}^{e}$',
    'QArgSim_max_exact_sbert_full_document' : 'QArgSim$_{max}^{e}$',

    #'QArgSim_max_sbert' : 'QArgSim$_{max}$',
    'QArgSim_max_sbert_full_document' : 'QArgSim$_{max}$',

    #'QArgSim_mean_exact_sbert' : 'QArgSim$_{mean}^{e}$',
    'QArgSim_mean_exact_sbert_full_document' : 'QArgSim$_{mean}^{e}$',

    #'QArgSim_mean_sbert' : 'QArgSim$_{mean}$',
    'QArgSim_mean_sbert_full_document' : 'QArgSim$_{mean}$',

}

arg_translate_dict_tmp.update({

    'ANTI_REG_f' : 'ANTI\_REG$_{f}$',
    'ANTI_REG_w' : 'ANTI\_REG$_{w}$',
    'ASPECT_REG_f' : 'ASPECT\_REG$_{f}$',
    'ASPECT_REG_w' : 'ASPECT\_REG$_{w}$',

        'LEN_AND' : 'LEN\_AND',
    'LEN_DIV' : 'LEN\_DIV',
    'LEN_M_AND' : 'LEN\_M\_AND',
    'LEN_M_TDC' : 'LEN\_M\_TDC',

    'M_AND' : 'M\_AND',
    'M_TDC' : 'M\_TDC',

    'REG_f' : 'REG$_{f}$',
    'REG_w' : 'REG$_{w}$',

    'RS_BM25' : 'RS\_BM25',
        'RS_PL2' : 'RS\_PL2',

        'RS_QL' : 'RS\_QL',
        'RS_TF' : 'RS\_TF',

'RS_TF_IDF' : 'RS\_TF\_IDF',

    'STMC1_sbert' : 'STMC1$_{s}$',
    'STMC1_f' : 'STMC1$_{f}$',
    'STMC1_w' : 'STMC1$_{w}$',

    'STMC2_f' : 'STMC2$_{f}$',
    'STMC2_w' : 'STMC2$_{w}$',

    'TF_LNC' : 'TF\_LNC',

})

arg_translate_dict_tmp.update({
'elrond' : 'Elrond',
'pippin-took' : 'Took',
'dread-pirate-roberts' : 'Roberts',
'asterix' : 'Asterix',
'robin-hood' : 'Hood',
'skeletor' : 'Skeletor',
'shanks' : 'Shanks',
'luke-skywalker' : 'Skywalker',
'deadpool' : 'Deadpool',
'heimdall' : 'Heimdall',
'athos' : 'Athos',
'jean-pierre-polnareff' : 'Polnareff',
'goemon-ishikawa' : 'Ishikawa',
'baseline-dirichlet'    : 'DirichletLM',
})

def arg_translate_dict(x):
    if x in arg_translate_dict_tmp:
        return arg_translate_dict_tmp[x]
    return x