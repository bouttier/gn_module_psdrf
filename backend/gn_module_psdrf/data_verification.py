import json
import pandas as pd
import numpy as np
import datetime
import re

from pathlib import Path

# Fonction principale de vérification des données du PSDRF
def data_verification(data):
  # TODO: Expliquer à quoi sert cette variable
  Test = 0

  # TODO: Expliquer à quoi sert ce tableau une fois le fichier R traduit
  error = []

  tableDict = {}
  # Initialisation des données du dispositif testée dans des dataframes Pandas
  Placettes = pd.json_normalize(data[0]) 
  Cycles = pd.json_normalize(data[1])
  Arbres = pd.json_normalize(data[2])
  Regeneration = pd.json_normalize(data[3])
  Transect = pd.json_normalize(data[4])
  BMSsup30 = pd.json_normalize(data[5])
  Reperes = pd.json_normalize(data[6])
  print(data)

  print(Transect)

  # Trouver le chemin d'accès au dossier data, qui contient les tables nécessaires aux tests
  ROOT_DIR_PSDRF = Path(__file__).absolute().parent.parent
  DATA_DIR_PSDRF = ROOT_DIR_PSDRF / "data"

  #chargement des tables nécessaires aux tests 
  CodeEssence = pd.read_pickle(DATA_DIR_PSDRF / 'CodeEssence')
  CyclesCodes = pd.read_pickle(DATA_DIR_PSDRF / 'CyclesCodes')
  Dispositifs = pd.read_pickle(DATA_DIR_PSDRF / 'Dispositifs')
  CodeDurete = pd.read_pickle(DATA_DIR_PSDRF / 'CodeDurete')
  CodeTypoArbres = pd.read_pickle(DATA_DIR_PSDRF / 'CodeTypoArbres')
  CodeEcologie = pd.read_pickle(DATA_DIR_PSDRF / 'CodeEcologie')
  CodeEcorce = pd.read_pickle(DATA_DIR_PSDRF / 'CodeEcorce')
  EssReg = pd.read_pickle(DATA_DIR_PSDRF / 'EssReg')
  Communes = pd.read_pickle(DATA_DIR_PSDRF / 'Communes')
  Referents = pd.read_pickle(DATA_DIR_PSDRF / 'Referents')
  Tarifs = pd.read_pickle(DATA_DIR_PSDRF / 'Tarifs')

  An = datetime.datetime.now().year
  #Creation du tableau de vérification qui sera retourné:
  # - chaque élément du tableau correspond à une erreur différente
  # - errorList correspond à la liste des éléments qui ont cette erreur
  # - correctionList correspond aux solutions possible pour résoudre cette erreur
  verificationList = []
  correctionList = {}

  correctionList['StadeD'] = CodeDurete['Code'].tolist()
  correctionList['StadeD'].insert(0, None)
  correctionList['Essence'] = CodeEssence['Essence'].tolist()
  correctionList['Essence'].insert(0, None)
  correctionList['Type'] = CodeTypoArbres['Id'].tolist()
  correctionList['Type'].insert(0, None)
  correctionList['StadeE'] = CodeEcorce['Code'].tolist()
  correctionList['StadeE'].insert(0, None)
  correctionList['Ref_CodeEcolo'] = ["prosilva", "efi", "irstea"]
  correctionList['Ref_CodeEcolo'].insert(0, None)

  disp_num = Placettes["NumDisp"][0]
  last_cycle = Cycles[Cycles["NumDisp"] == disp_num]["Cycle"].max()

  tables =["Placettes", "Cycles", "Arbres", "Regeneration", 
         "Transect", "BMSsup30", "Reperes", 
         "CyclesCodes", "Dispositifs", 
         "EssReg", "Communes", "Referents", "Tarifs"] 


  #Tester si il n'y a pas de valeurs vitales nulles (Disp, Placette, Cycle)
  check_null_DPC(Placettes, "Placettes")
  check_null_DPC(Cycles, "Cycles")
  check_null_DPC(Arbres, "Arbres")
  check_null_DPC(Regeneration, "Regeneration")
  check_null_DPC(Transect, "Transect")
  check_null_DPC(BMSsup30, "BMSsup30")
  check_null_DPC(Reperes, "Reperes")
  check_null_DPC(CyclesCodes, "CyclesCodes")
  check_null_DPC(Dispositifs, "Dispositifs")
  check_null_DPC(EssReg, "EssReg")
  check_null_DPC(Communes, "Communes")
  check_null_DPC(Referents, "Referents")  
  check_null_DPC(Tarifs, "Tarifs")  

  Placettes = filter_by_disp(disp_num, last_cycle, Placettes, disp_num)
  Cycles = filter_by_disp(disp_num, last_cycle, Cycles, disp_num)
  Arbres = filter_by_disp(disp_num, last_cycle, Arbres, disp_num)
  Regeneration = filter_by_disp(disp_num, last_cycle, Regeneration, disp_num)
  Transect = filter_by_disp(disp_num, last_cycle, Transect, disp_num)
  BMSsup30 = filter_by_disp(disp_num, last_cycle, BMSsup30, disp_num)
  Reperes = filter_by_disp(disp_num, last_cycle, Reperes, disp_num)
  CyclesCodes = filter_by_disp(disp_num, last_cycle, CyclesCodes, disp_num)
  Dispositifs = filter_by_disp(disp_num, last_cycle, Dispositifs, disp_num)
  EssReg = filter_by_disp(disp_num, last_cycle, EssReg, disp_num)
  Communes = filter_by_disp(disp_num, last_cycle, Communes, disp_num)
  Referents = filter_by_disp(disp_num, last_cycle, Referents, disp_num)
  Tarifs = filter_by_disp(disp_num, last_cycle, Tarifs, disp_num)


  # Convertion de types
  # errors='ignore' permet de ne pas convertir si le type n'est pas convertible en nombre
  Arbres = Arbres.apply(pd.to_numeric, errors='ignore')
  BMSsup30 = BMSsup30.apply(pd.to_numeric, errors='ignore')
  Transect = Transect.apply(pd.to_numeric, errors='ignore')
  print(Transect["Angle"])
  Transect["Angle"]= Transect["Angle"].astype(int)


  
  soundness_code = "de décomposition"
  bark_code = "écorce"
  check_code_Error_List = check_code(CodeDurete, Arbres, soundness_code, "Arbres")
  if len(check_code_Error_List) >0:
    verificationList.append({'errorName': 'Contrôle Stade dans Arbres', 'errorText': 'Contrôle Stade dans Arbres', 'errorList': check_code_Error_List, 'errorType': 'PsdrfError'})

  #Appel des fonctions de test
  ###Table Arbres
  #Contrôle des essences rencontrées dans la table Arbres
  error_List_Temp = check_species(Arbres, CodeEssence, Test, "Arbres")
  if len(error_List_Temp) >0:
    verificationList.append({'errorName': 'Essence dans Arbres', 'errorText':"Essence dans Arbres", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})


  #Contrôle des sauts de cycles: Contrôle qu'il n'y ait pas de cycles qui sautent
  error = []
  a = Arbres.groupby("NumDisp").agg({'Cycle': lambda s: len(list(s.unique()))})
  b = Arbres.groupby("NumDisp").agg({'Cycle': lambda s: s.max()})
  if not a.equals(b):
    listCycle = Arbres.Cycle.unique()
    for index, row in b.iterrows():
      for i in range(row["Cycle"]):
        if not i in listCycle:
          err = {
            "message": "Le cycle"+ str(i) +" est sauté dans la table Arbres",
            "table": "Arbres", 
            "column": 'Cycle',
          }
          error.append(err)
  if len(error) >0:
    verificationList.append({'errorName': 'Cycles dans Arbres', 'errorText': 'Cycles dans Arbres', 'errorList': error})

  #Contrôle des valeurs dupliquées
  error = []
  df_Dupl_temp= Arbres[["NumDisp", "NumPlac", "NumArbre", "Cycle"]].sort_values(by=["NumDisp", "NumPlac", "NumArbre", "Cycle"])
  Arbres= Arbres.sort_values(by=["NumDisp", "NumPlac", "NumArbre", "Cycle"])
  df_Dupl = df_Dupl_temp[df_Dupl_temp.duplicated()]
  if not df_Dupl.empty:
    entire_df_Dupl = df_Dupl_temp[df_Dupl_temp.duplicated(keep=False)]
    listDupl = entire_df_Dupl.groupby(list(df_Dupl_temp)).apply(lambda x: list(x.index)).tolist()
    i = 0
    error_List_Temp = []
    for index, row in df_Dupl.iterrows():
      valuesDupl = entire_df_Dupl.loc[listDupl[i]]
      err = {
          "message": "L'Arbre "+ str(row["NumArbre"]) +" au cycle "+ str(row["Cycle"]) +" apparaît plusieurs fois dans la table Arbres",
          "table": "Arbres",
          "column": ["NumDisp", "NumPlac", "NumArbre", "Cycle"],
          "row": listDupl[i], 
          "value": valuesDupl.to_json(orient='records'),
        }
      i = i + 1
      error_List_Temp.append(err)
    verificationList.append({'errorName': 'Duplication dans Arbres', 'errorText':'Lignes dupliquées dans la table Arbres', 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})


  # 5/ Contrôle du suivi des arbres entre les différents inventaires
  #le contrôle est impossible si il existe des doublons NumDisp + NumPlac + NumArbre
  elif last_cycle > 1:
    tArbres = Arbres[["NumDisp", "NumPlac", "NumArbre", "Cycle", "Essence", "Azimut", "Dist"]]
    t = pd.melt(tArbres, id_vars=["NumDisp", "NumPlac", "NumArbre", "Cycle"], value_vars=["Essence", "Azimut", "Dist"], ignore_index=False)

    #On utilise la fonction first car il n'y a pas de duplicate dans notre cas. 
    t = t.pivot_table(index=["NumDisp", "NumPlac", "NumArbre", "variable"], columns='Cycle', values='value', aggfunc=['first', lambda x: x.index[0]]).reset_index()

    t = t.sort_values(by=["NumDisp", "NumPlac", "NumArbre", "variable"])

    # Note : on distingue quand il y a 2 cycles et 1 seul
    #
    # Cas où un arbre présent au cycle 1, disparaît au cycle 2 et réapparaît au cycle3
    if last_cycle > 2:
      pos_Error1 = []
      # On prend le dernier cycle et on considères les arbres non coupés (non Na)
      df_temp1 = t[~t.iloc[:,t.shape[1]-1].isna()]
      for i in range(5, t.shape[1]):
        pos_Error1 =  np.concatenate((pos_Error1, np.array(np.where(df_temp1.iloc[:, i] != df_temp1.iloc[:, i-1])).tolist()[0]))
      pos_Error1 = np.unique(pos_Error1)
      df_Error1 = df_temp1.iloc[pos_Error1, : ]

      pos_Error2= []
      # On prend le dernier cycle et on considères les arbres coupés (Na)
      df_temp2 = t[t.iloc[:,t.shape[1]-1].isna()]
      for i in range(5, t.shape[1]-1):
        # Si arbre coupé au dernier cycle, les autres valeurs doivent être identiques
        pos_Error2 =  np.concatenate((pos_Error2, np.array(np.where(df_temp2.iloc[:, i] != df_temp2.iloc[:, i-1])).tolist()[0]))
      pos_Error2 = np.unique(pos_Error2)
      df_Error2 = df_temp2.iloc[pos_Error2, : ]

      df_Error = np.concatenate((df_Error1, df_Error2))

    # Cas où on n'a que 2 cycles
    else:
      # pos_Error = np.where(~(pd.isnull(t.shape[1])) & ((t.iloc[:, 4]) != (t.iloc[:,5])))
      # pos_Error = np.unique(pos_Error)
      # df_Error = t.iloc[pos_Error, : ]

      temp1 = t[(~t.iloc[:,4].isna()) & (~t.iloc[:,5].isna())]
      pos_Error = np.where(temp1.iloc[:,4] != temp1.iloc[:,5])
      pos_Error = np.unique(pos_Error)
      df_Error = temp1.iloc[pos_Error, : ]
        
    if df_Error.shape[0] > 0 :
      error_List_Temp = []
      for index, row in df_Error.iterrows():
        # valuesDupl = df_Error.loc[listDupl[i]]
        tValues = tArbres[["NumArbre", "Cycle", str(row["variable"].item())]].loc[[int(x) for x in row["<lambda>"].values]]
        err = {
            "message": "Incohérence(s) relevée(s) sur les valeurs "+ str(row["variable"].item()) +" pour l'arbre numéro "+ str(row["NumArbre"].item()) + " de la placette numéro " + str(row["NumPlac"].item()),
            "table": "Arbres",
            "column": [ "NumArbre", "Cycle", str(row["variable"].item())],
            "row": [int(x) for x in row["<lambda>"].values], 
            "value": tValues.to_json(orient='records'),
          }
        error_List_Temp.append(err)
      verificationList.append({'errorName': "Incohérence dans Arbres", 'errorText': "Incohérence(s) relevée(s) sur les valeurs d'Essence, Azimut et Dist entre les différents inventaires", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})




    # -- Contrôle des valeurs d'accroissement en diamètre
    # Pour les Arbres vivants
    t = Arbres[["NumDisp", "NumPlac", "NumArbre", "Cycle", "Diam1", "Diam2", "Type"]]
    tArbres = t[t["Type"].isna()]
    t = pd.melt(tArbres, id_vars=["NumDisp", "NumPlac", "NumArbre", "Cycle", "Type"], value_vars=["Diam1", "Diam2"], ignore_index=False)
    t = t.pivot_table(index=["NumDisp", "NumPlac", "NumArbre", "variable"], columns='Cycle',values='value', aggfunc=['first', lambda x: x.index[0]]).reset_index()
    t = t.sort_values(by=["NumDisp", "NumPlac", "NumArbre", "variable"])

    if last_cycle > 2:
      #Sous ensemble des arbres non coupés au dernier cycle
      pos_Error1 = []
      df_temp1 = t[~t.iloc[:,t.shape[1]-1].isna()] # On supprime les arbres dont la dernière valeur est vide (arbre coupé)
      for i in range(5, t.shape[1]):
        pos_Error1 =  np.concatenate((pos_Error1, np.array(np.where(df_temp1.iloc[:, i] < df_temp1.iloc[:, i-1])).tolist()[0]))
      pos_Error1 = np.unique(pos_Error1)
      df_Error1 = df_temp1.iloc[pos_Error1, : ]


      #Sous ensemble des arbres coupés au dernier cycle
      pos_Error2 = []
      df_temp2 = t[t.iloc[:,t.shape[1]-1].isna()]
      for i in range(5, t.shape[1]-1):
          # Si arbre coupé au dernier cycle, les autres valeurs doivent être croissantes au cours du temps
          pos_Error2 =  np.concatenate((pos_Error2, np.array(np.where(df_temp2.iloc[:, i] < df_temp2.iloc[:, i-1])).tolist()[0]))
      pos_Error2 = np.unique(pos_Error2)
      df_Error2 = df_temp2.iloc[pos_Error2, : ]

      df_Error = np.concatenate((df_Error1, df_Error2))

    else:
      pos_Error = np.where(~(pd.isnull(t.shape[1])) & ((t.iloc[:, 4]) > (t.iloc[:,5])))
      pos_Error = np.unique(pos_Error)
      df_Error = t.iloc[pos_Error, : ]

    if df_Error.shape[0] > 0 :
      error_List_Temp = []
      for index, row in df_Error.iterrows():
        # valuesDupl = df_Error.loc[listDupl[i]]
        tValues = tArbres[["NumArbre", "Cycle", str(row["variable"].item())]].loc[[int(x) for x in row["<lambda>"].values],:]
        err = {
            "message": "Accroissement(s) sur le "+ str(row["variable"].item()) +" négatif(s)  pour l'arbre numéro "+ str(row["NumArbre"].item()) + " de la placette numéro " + str(row["NumPlac"].item()),
            "table": "Arbres",
            "column": [ "NumArbre", "Cycle", str(row["variable"].item())],
            "row": [int(x) for x in row["<lambda>"].values], 
            "value": tValues.to_json(orient='records'),
          }
        error_List_Temp.append(err)
      verificationList.append({'errorName': "Accroissement négatif dans Arbres" , 'errorText': "Accroissement(s) sur le diamètre négatif(s) constaté(s) sur la population d'arbres vivants entre les différents inventaires", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})





    # Pour les Arbres morts sur pied
    tArbres = Arbres[["NumDisp", "NumPlac", "NumArbre", "Cycle", "Diam1", "Diam2", "Type"]]
    t = tArbres[~tArbres["Type"].isna()]
    t = pd.melt(t, id_vars=["NumDisp", "NumPlac", "NumArbre", "Cycle", "Type"], value_vars=["Diam1", "Diam2"], ignore_index=False)
    t = t.pivot_table(index=["NumDisp", "NumPlac", "NumArbre", "Type", "variable"], columns='Cycle',values='value', aggfunc=['first', lambda x: x.index[0]]).reset_index()
    t = t.sort_values(by=["NumDisp", "NumPlac", "NumArbre", "variable"])
    df_temp = t
    # Note : on distingue quand il y a 2 cycles et 1 seul
    if last_cycle > 2 : # Cas où un arbre présent au cycle 1, disparaît au cycle 2 et réapparaît au cycle3
      # BMP doivent avoir été présent au passage précédent :
      pos_Error = []
      for i in range(6, t.shape[1]-1):
        # toutes les valeurs doivent être décroissantes au cours du temps
        pos_Error = np.concatenate((pos_Error, np.array(np.where(df_temp.iloc[:, i] > df_temp.iloc[:, i-1])).tolist()[0]))
        pos_Error = np.unique(pos_Error)
        df_Error = df_temp.iloc[pos_Error, : ]
    else:
      pos_Error = np.where(~(pd.isnull(t.iloc[:, 5])) & ~(pd.isnull(t.iloc[:, 6])) & ((t.iloc[:, 5]) < (t.iloc[:,6])) )
      pos_Error = np.unique(pos_Error)
      df_Error = df_temp.iloc[pos_Error, : ]   

    if df_Error.shape[0] > 0 :
      error_List_Temp = []
      for index, row in df_Error.iterrows():
        # valuesDupl = df_Error.loc[listDupl[i]]
        tValues = tArbres[["NumArbre", "Cycle", "Type", str(row["variable"].item())]].loc[[int(x) for x in row["<lambda>"].values],:]
        err = {
            "message": "Accroissement(s) sur le "+ str(row["variable"].item()) +" positif(s)  pour l'arbre numéro "+ str(row["NumArbre"].item()) + " de la placette numéro " + str(row["NumPlac"].item()),
            "table": "Arbres",
            "column": [ "NumArbre", "Cycle","Type", str(row["variable"].item())],
            "row": [int(x) for x in row["<lambda>"].values], 
            "value": tValues.to_json(orient='records'),
          }
        error_List_Temp.append(err)
      verificationList.append({'errorName': "Accroissement positif BMP dans Arbres", 'errorText': "Accroissement(s) sur le diamètre positif(s) constaté(s) sur la population d'arbres morts sur pied entre les différents inventaires.", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})



    # ----- Contrôle sur les écarts de diamètre entre les cycles trop importants
    t = Arbres[["NumDisp", "NumPlac", "NumArbre", "Cycle", "Diam1", "Diam2", "Type"]]
    t = pd.melt(t, id_vars=["NumDisp", "NumPlac", "NumArbre", "Cycle", "Type"], value_vars=["Diam1", "Diam2"], ignore_index=False)
    t = t.pivot_table(index=["NumDisp", "NumPlac", "NumArbre", "variable"], columns='Cycle',values='value', aggfunc=['first', lambda x: x.index[0]]).reset_index()
    t = t.sort_values(by=["NumDisp", "NumPlac", "NumArbre", "variable"])

    pos = []
    for i in range(1, last_cycle) :
      t["temp"] = abs(t.iloc[:, i + 4] - t.iloc[: , i +3])
      error_trees = t[t["temp"] > 15]
    if error_trees.shape[0] > 0 :
      error_List_Temp = []
      for index, row in error_trees.iterrows():
        tValues = tArbres[["NumArbre", "Cycle", str(row["variable"].item())]].loc[[int(x) for x in row["<lambda>"].values],:]
        err = {
            "message": "Valeur d'accroissement trop importante pour le "+ str(row["variable"].item()) +" de l'arbre numéro "+ str(row["NumArbre"].item()) + " de la placette numéro " + str(row["NumPlac"].item()),
            "table": "Arbres",
            "column": [ "NumArbre", "Cycle", str(row["variable"].item())],
            "row": [int(x) for x in row["<lambda>"].values], 
            "value": tValues.to_json(orient='records'),
          }
        error_List_Temp.append(err)
      verificationList.append({'errorName': "Accroissement anormal dans Arbres", 'errorText': "Valeur(s) d'accroissement en diamètre trop importante(s) détectée(s) (seuil à 15 cm entre les 2 inventaires", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})

  # ##### 6/ Incohérence type de Bois Mort sur Pied et de Taillis #####
  # -- contrôle des types de bois mort sur pied :
  temp = Arbres[(~Arbres["Type"].isna()) & (~Arbres.Type.isin(CodeTypoArbres.Id))]
  # temp = temp.drop_duplicates()
  # temp = type_list[['NumPlac', "NumArbre", "Cycle", "Type"]]
  if not temp.empty:
    error_List_Temp = []
    for index, row in temp.iterrows():
      err= {
        "message": "Le type "+ str(int(row["Type"])) + " figure dans la table Arbres mais ne figure pas dans la table CodeTypoArbres (fichier administrateur) ",
        "table": "Arbres",
        "column": ['Type'],
        "row": [index],
        "value": temp.loc[[index],:].to_json(orient='records'),
      }
      error_List_Temp.append(err)
    verificationList.append({'errorName': 'Types dans Arbres', 'errorText': 'Types dans Arbres','errorList': error_List_Temp,  'errorType': 'PsdrfError'})

  # Souches de plus de 1.30m
  temp = Arbres[(Arbres["Haut"] > 1.30) & (Arbres["Type"]==3)]
  temp = temp[["NumPlac", "NumArbre", "Type", "Haut"]]
  if not temp.empty:
    error_List_Temp=[]
    for index, row in temp.iterrows():
      err = {
          "message": "La souche  "+ str(int(row["NumArbre"])) +" de la placette "+ str(int(row["NumPlac"])) + " mesure plus d'1,30m.",
          "table": "Arbres",
          "column": [ "NumArbre", "Type", "Haut"],
          "row": [index], 
          "value": temp.loc[[index],:].to_json(orient='records'),
        }
      error_List_Temp.append(err)
    verificationList.append({'errorName': "Souche(s) incohérente(s) dans Arbres", 'errorText': "BMP classé(s) en Type 3 (souche) et faisant strictement plus d'1,30m. Impossible dans le PSDRF.", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})


  #Arbres ou chandelles < 1.30m
  temp = Arbres[(Arbres["Haut"] < 1.30) & (~Arbres.Type.isin([3, 4, 5]))]
  temp = temp[["NumPlac", "NumArbre", "Type", "Haut"]]
  if not temp.empty:
    error_List_Temp=[]
    for index, row in temp.iterrows():
      err = {
          "message": "L'arbre  "+ str(int(row["NumArbre"])) +" de la placette "+ str(int(row["NumPlac"])) + " mesure moins d'1,30m.",
          "table": "Arbres",
          "column": [ "NumArbre", "Type", "Haut"],
          "row": [index], 
          "value": temp.loc[[index],:].to_json(orient='records'),
        }
      error_List_Temp.append(err)
    verificationList.append({'errorName': "Arbre(s) incohérent(s) dans Arbres", 'errorText': "Il y a des BMP classés en 'Arbre' ou en 'Chandelle' et faisant moins d'1,30m. Impossible dans le PSDRF", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})


  # Incohérences sur les données Type - Haut - StadeD - StadeE des BMP 
  ListDisp_Verif = []
  BMP_Temp = Arbres[~Arbres["Type"].isna() | ~Arbres["Haut"].isna() | ~Arbres["StadeD"].isna() | ~Arbres["StadeE"].isna()]
  BMP_Temp = BMP_Temp[BMP_Temp["Type"].isna() | ((BMP_Temp["Haut"].isna()) & (BMP_Temp["Type"] != 1)) | BMP_Temp["StadeD"].isna() | BMP_Temp["StadeE"].isna()]
  BMP_Temp = BMP_Temp[[ "NumPlac", "NumArbre", "Type", "Haut", "StadeD", "StadeE"]]
  if not BMP_Temp.empty:
    error_List_Temp=[]
    for index, row in BMP_Temp.iterrows():
      err = {
          "message": "Information manquante pour l'arbre "+ str(int(row["NumArbre"])) +" de la placette "+ str(int(row["NumPlac"])),
          "table": "Arbres",
          "column": [ "NumArbre", "Type", "Haut", "StadeD", "StadeE"],
          "row": [index], 
          "value": BMP_Temp.loc[[index],:].to_json(orient='records'),
        }
      error_List_Temp.append(err)
    verificationList.append({'errorName': "Information(s) manquante(s) dans Arbres", 'errorText': "Information(s) manquante(s) pour les BMP", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})

  # Incohérences sur les données de Taillis 
  Taillis_Temp = Arbres[~Arbres.Taillis.isin(["t", "f", pd.NA])]
  Taillis_Temp = Taillis_Temp[[ "NumPlac", "NumArbre", "Taillis"]]
  if not Taillis_Temp.empty:
    error_List_Temp=[]
    for index, row in Taillis_Temp.iterrows():
      err = {
          "message": "Information incorrectes dans la colonne Taillis pour l'arbre "+ str(int(row["NumArbre"])) +" de la placette "+ str(int(row["NumPlac"])),
          "table": "Arbres",
          "column": [ "NumArbre", "Taillis"],
          "row": [index], 
          "value": Taillis_Temp.loc[[index],:].to_json(orient='records'),
        }
      error_List_Temp.append(err)
    verificationList.append({'errorName': "Taillis incorrecte(s) dans Arbres", 'errorText': "Il y a des informations incorrectes dans la colonne Taillis. Rappel : seules notations acceptées (hormis valeurs vides) = 't' ou 'f'", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})


  ##### 7/ Contrôle des valeurs absentes #####
  # -- contrôle présence de Diam2
  Empty_temp = Arbres[(Arbres["Diam1"]>30) & (Arbres["Diam2"].isna()) & (Arbres["Type"].isna())]
  Empty_temp = Empty_temp[[ "NumPlac", "NumArbre", "Diam1", "Diam2"]]
  if not Empty_temp.empty:
    error_List_Temp=[]
    for index, row in Empty_temp.iterrows():
      err = {
          "message": "Le Diam2 de l'arbre "+ str(int(row["NumArbre"])) +" de la placette "+ str(int(row["NumPlac"])) + " n'est pas renseigné.",
          "table": "Arbres",
          "column": [ "NumArbre", "Diam1", "Diam2"],
          "row": [index], 
          "value": Empty_temp.loc[[index],:].to_json(orient='records'),
        }
      error_List_Temp.append(err)
    verificationList.append({'errorName': "Diam2 non renseigné", "errorText": "Diam2 vides pour des arbres vivants de Diam1 > 30 cm", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})


  # -- autres variables
  # # repérages des vides
  Vital = Arbres[ Arbres["NumArbre"].isna() |  Arbres["Essence"].isna() | Arbres["Azimut"].isna() | Arbres["Dist"].isna() | Arbres["Diam1"].isna()]
  Vital = Vital[[ "NumPlac", "NumArbre", "Essence", "Azimut", "Dist", "Diam1"]]
  if not Vital.empty:
    error_List_Temp=[]
    for index, row in Vital.iterrows():
      err = {
          "message": "Une/des colonne(s) de l'arbre "+ str(int(row["NumArbre"])) +" de la placette "+ str(int(row["NumPlac"])) + " ne sont pas renseignées.",
          "table": "Arbres",
          "column": ["NumArbre", "Essence", "Azimut", "Dist", "Diam1"],
          "row": [index], 
          "value": Vital.loc[[index],:].to_json(orient='records'),
        }
      error_List_Temp.append(err)
    verificationList.append({'errorName': "Informations manquantes dans Arbres", 'errorText': "Il manque des informations à des colonne(s) dans la table Arbre", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})

  # ---------- Contrôle des codes écologiques : ---------- #
  Table_temp = Arbres[~Arbres["CodeEcolo"].isna() & Arbres["Ref_CodeEcolo"].isna()]
  Table_temp = Table_temp[[ "NumPlac", "NumArbre", "CodeEcolo", "Ref_CodeEcolo" ]]
  if not Table_temp.empty:
    error_List_Temp=[]
    for index, row in Table_temp.iterrows():
      err = {
          "message": "L'arbre "+ str(int(row["NumArbre"])) +" de la placette "+ str(int(row["NumPlac"])) + " n'a pas de Ref_CodeEcolo.",
          "table": "Arbres",
          "column": [ "NumPlac", "NumArbre", "CodeEcolo", "Ref_CodeEcolo" ],
          "row": [index], 
          "value": Table_temp.loc[[index],:].to_json(orient='records'),
        }
      error_List_Temp.append(err)
    verificationList.append({'errorName': "DMH sans référence de codification", 'errorText': "Il y a des arbres portant des DMH sans référence de codification renseignée (Ref_CodeEcolo vide pour CodeEcolo non vide)", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})


  # ----- CodeEcolo non reconnus
  df_Codes = Arbres[~Arbres["Ref_CodeEcolo"].isna()]
  posProSilva = df_Codes[(df_Codes["Ref_CodeEcolo"].str.lower()=="prosilva") & 
    (~df_Codes["NumDisp"].isna()) & 
    (~df_Codes["NumPlac"].isna()) & 
    (~df_Codes["NumArbre"].isna()) & 
    (~df_Codes["CodeEcolo"].isna()) ]
  posEFI = df_Codes[(df_Codes["Ref_CodeEcolo"].str.lower()=="efi") & 
    ~df_Codes["NumDisp"].isna() & 
    ~df_Codes["NumPlac"].isna() & 
    ~df_Codes["NumArbre"].isna() & 
    ~df_Codes["CodeEcolo"].isna() ]
  posIRSTEA = df_Codes[(df_Codes["Ref_CodeEcolo"].str.lower()=="irstea") & 
    ~df_Codes["NumDisp"].isna() & 
    ~df_Codes["NumPlac"].isna() & 
    ~df_Codes["NumArbre"].isna() & 
    ~df_Codes["CodeEcolo"].isna() ]
  posUnknown = df_Codes[(~(df_Codes["Ref_CodeEcolo"].str.lower()=="irstea")) & 
    (~(df_Codes["Ref_CodeEcolo"].str.lower()=="efi")) & 
    (~(df_Codes["Ref_CodeEcolo"].str.lower()=="afi")) & 
    (~(df_Codes["Ref_CodeEcolo"].str.lower()=="engref")) & 
    (~(df_Codes["Ref_CodeEcolo"].str.lower()=="prosilva")) & 
    (~df_Codes["NumDisp"].isna()) & 
    (~df_Codes["NumPlac"].isna()) & 
    (~df_Codes["NumArbre"].isna()) & 
    (~df_Codes["CodeEcolo"].isna()) ]




  # --- Codification ProSilva
  if not posProSilva.empty:
    posProSilva_temp = posProSilva
    posProSilva = posProSilva.assign(CodeEcolo = posProSilva["CodeEcolo"].astype(str).str.split("-"))
    posProSilva["CodeEcolo"]= posProSilva["CodeEcolo"].apply(set)
    Prosilva_codes = (set(CodeEcologie[CodeEcologie["Codification"]=="prosilva"]["Code"].apply(str)))
    #On utilise des set afin de pouvoir utiliser "<=" qui est l'équivalent de "issubset"
    temp = posProSilva[[(not (x <= Prosilva_codes)) for x in posProSilva["CodeEcolo"]]]
    if not temp.empty:
      error_List_Temp=[]
      for index, row in temp.iterrows():
        err = {
            "message": "Un/Plusieurs codes DMH n'est/ne sont pas reconnus pour l'arbre "+ str(int(row["NumArbre"])) +" de la placette "+ str(int(row["NumPlac"])),
            "table": "Arbres",
            "column": [ "NumPlac", "NumArbre", "CodeEcolo", "Ref_CodeEcolo" ],
            "row": [index], 
            "value": posProSilva_temp.loc[[index],:].to_json(orient='records'),
          }
        error_List_Temp.append(err)
      verificationList.append({'errorName': 'Code(s) DMH Prosilva non reconnu(s)', 'errorText': "Il y a des codes DMH référencés ProSilva qui ne sont pas reconnus", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})

  # --- Codification EFI
  if not posEFI.empty:
    posEFI_temp = posEFI
    posEFI = posEFI.assign(CodeEcolo = posEFI["CodeEcolo"].str.upper().astype(str).str.split("-"))
    posEFI["CodeEcolo"]= posEFI["CodeEcolo"].apply(set)
    EFI_codes = (set(CodeEcologie[CodeEcologie["Codification"]=="EFI"]["Code"].apply(str)))
    temp = posEFI[[(not (x <= EFI_codes)) for x in posEFI["CodeEcolo"]]]
    if not temp.empty:
      error_List_Temp=[]
      for index, row in temp.iterrows():
        err = {
            "message": "Un/Plusieurs codes DMH n'est/ne sont pas reconnus pour l'arbre "+ str(int(row["NumArbre"])) +" de la placette "+ str(int(row["NumPlac"])),
            "table": "Arbres",
            "column": [ "NumPlac", "NumArbre", "CodeEcolo", "Ref_CodeEcolo" ],
            "row": [index], 
            "value": posEFI_temp.loc[[index],:].to_json(orient='records'),
          }
        error_List_Temp.append(err)
      verificationList.append({'errorName': 'Code(s) DMH EFI non reconnu(s)', 'errorText': "Il y a des codes DMH référencés EFI qui ne sont pas reconnus", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})


  # --- Codification IRSTEA
  if not posIRSTEA.empty:
    posIRSTEA_temp = posIRSTEA
    IRSTEA_codes = CodeEcologie[CodeEcologie["Codification"]=="IRSTEA"]["Code"].astype(str).str.lower()
    posIRSTEA = posIRSTEA.assign(CodeEcolo = posIRSTEA["CodeEcolo"].astype(str).str.lower().str.split("-"))
    IRSTEA_mask = [(not pd.Series(s).str.contains(('(?![0-9])|(?<![0-9])'.join(IRSTEA_codes))).all()) for s in posIRSTEA["CodeEcolo"]]
    temp = posIRSTEA[IRSTEA_mask]
    if not temp.empty:
      error_List_Temp=[]
      for index, row in temp.iterrows():
        err = {
            "message": "Un/Plusieurs codes DMH n'est/ne sont pas reconnus pour l'arbre "+ str(int(row["NumArbre"])) +" de la placette "+ str(int(row["NumPlac"])),
            "table": "Arbres",
            "column": [ "NumPlac", "NumArbre", "CodeEcolo", "Ref_CodeEcolo" ],
            "row": [index], 
            "value": posIRSTEA_temp.loc[[index],:].to_json(orient='records'),
          }
        error_List_Temp.append(err)
      verificationList.append({'errorName': 'Code(s) DMH IRSTEA non reconnu(s)', 'errorText': "Il y a des codes DMH référencés IRSTEA qui ne sont pas reconnus", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})

  # --- Codification non reconnue
  if not posUnknown.empty:
    error_List_Temp=[]
    for index, row in posUnknown.iterrows():
      err = {
          "message": "Références à des codes écologiques non reconnues pour l'arbre "+ str(int(row["NumArbre"])) +" de la placette "+ str(int(row["NumPlac"])),
          "table": "Arbres",
          "column": [ "NumPlac", "NumArbre", "Ref_CodeEcolo" ],
          "row": [index], 
          "value": posUnknown.loc[[index],:].to_json(orient='records'),
        }
      error_List_Temp.append(err)
    verificationList.append({'errorName': 'Code(s) écologiques non reconnu(s)', 'errorText': "Il y a des références à des codifications de codes écologiques non reconnues. Rappel : les seules codifications reconnues sont celles de ProSilva, de l'IRSTEA et de l'EFI.", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})



  ###Table BMSsup30
  v = BMSsup30["Essence"].drop_duplicates()
 
  # Contrôle des stades de décomposition
  soundness_code = "de décomposition"
  error_List_Temp = check_code(CodeDurete, BMSsup30, soundness_code, "BMSsup30")
  if len(error_List_Temp) >0:
    verificationList.append({'errorName': 'Contrôle Stade de décomposition non reconnu(s)', 'errorText': 'Contrôle Stade de décomposition dans BMSsup30', 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})


  # Contrôle des stades de d'écorce'
  bark_code = "écorce"
  error_List_Temp = check_code(CodeEcorce, BMSsup30, bark_code, "BMSsup30")
  if len(error_List_Temp) >0:
    verificationList.append({'errorName': "Contrôle Stade d'écorce non reconnu", 'errorText':  "Contrôle Stade d'écorce dans BMSsup30", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})


  # Contrôle des numéros d'inventaire
  check_cycle_Error_List = check_cycle(BMSsup30, Test, CyclesCodes, "BMSsup30", An, Dispositifs)
  if len(check_cycle_Error_List) >0:
    verificationList.append({'errorName': "Contrôle des cycles dans BMSsup30", 'errorText': 'Contrôle des cycles dans BMSsup30', 'errorList' : check_cycle_Error_List, 'errorType': 'PsdrfError'})


  # Contrôle des valeurs vides des variables :
  tBMSsup30 = BMSsup30[["NumDisp", "NumPlac", "NumArbre", "Cycle", "Essence", "Azimut", "Dist"]]
  Vital = BMSsup30[ BMSsup30["Id"].isna() |  BMSsup30["Essence"].isna() | BMSsup30["DiamMed"].isna() | BMSsup30["Longueur"].isna() | BMSsup30["StadeD"].isna() | BMSsup30["StadeE"].isna()]
  Vital = Vital[["NumPlac", "NumArbre", "Id", "Essence", "DiamMed", "Longueur", "StadeD", "StadeE"]]
  if not Vital.empty:
    error_List_Temp=[]
    for index, row in Vital.iterrows():
      err = {
          "message": "Une/des colonne(s) de l'arbre "+ str(int(row["NumArbre"])) +" de la placette "+ str(int(row["NumPlac"])) + " n'est/ne sont pas renseignées.",
          "table": "BMSsup30",
          "column": ["NumArbre", "Id", "Essence", "DiamMed", "Longueur", "StadeD", "StadeE"],
          "row": [index], 
          "value": Vital.loc[[index],:].to_json(orient='records'),
        }
      error_List_Temp.append(err)
    verificationList.append({'errorName': "Informations manquantes dans BMSsup30", 'errorText': "Il manque des informations à des colonne(s) dans la table BMSsup30", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})

  # Contrôle des valeurs dupliquées
  error = []
  df_Dupl_temp= BMSsup30[["NumDisp", "NumPlac", "Id", "Cycle"]].sort_values(by=["NumDisp", "NumPlac", "Id", "Cycle"])
  BMSsup30= BMSsup30.sort_values(by=["NumDisp", "NumPlac", "Id", "Cycle"])
  df_Dupl = df_Dupl_temp[df_Dupl_temp.duplicated()]
  if not df_Dupl.empty:
    entire_df_Dupl = df_Dupl_temp[df_Dupl_temp.duplicated(keep=False)]
    listDupl = entire_df_Dupl.groupby(list(df_Dupl_temp)).apply(lambda x: list(x.index)).tolist()
    i = 0
    error_List_Temp = []
    for index, row in df_Dupl.iterrows():
      valuesDupl = entire_df_Dupl.loc[listDupl[i]]
      err = {
          "message": "L'Arbre "+ str(row["Id"])+" de la placette "+ str(int(row["NumPlac"])) +" au cycle "+ str(row["Cycle"]) +" apparaît plusieurs fois dans la table BMSsup30",
          "table": "BMSsup30",
          "column": ["NumDisp", "NumPlac", "Id", "Cycle"],
          "row": listDupl[i], 
          "value": valuesDupl.to_json(orient='records'),
        }
      i = i + 1
      error_List_Temp.append(err)
    verificationList.append({'errorName': "Duplication dans BMSsup30", 'errorText': 'Lignes dupliquées dans la table BMSsup30', 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})
  BMSsup30[["DiamFin", "DiamMed", "DiamIni"]] = BMSsup30[["DiamFin", "DiamMed", "DiamIni"]].apply(pd.to_numeric)


  # Contrôle des diamètres
  # ----- Contrôle DiamFin > 30 : 
  temp = BMSsup30[((BMSsup30["DiamFin"] < 30) & (BMSsup30["DiamFin"] != 0)) | ((BMSsup30["DiamMed"] < 30) & (BMSsup30["DiamMed"] != 0)) | ((BMSsup30["DiamIni"] < 30) & (BMSsup30["DiamIni"] != 0))]
  temp = temp[["NumPlac", "Id", "DiamFin", "DiamMed", "DiamIni"]]
  if not temp.empty:
    error_List_Temp=[]
    for index, row in temp.iterrows():
      err = {
          "message": "Le billon  "+ str(int(row["Id"])) +" de la placette "+ str(int(row["NumPlac"])) + " mesure moins de 30cm.",
          "table": "BMSsup30",
          "column": ["NumPlac", "Id", "DiamFin", "DiamMed", "DiamIni"],
          "row": [index], 
          "value": temp.loc[[index],:].to_json(orient='records'),
        }
      error_List_Temp.append(err)
    verificationList.append({'errorName': "Diamètre trop petit dans BMSsup30", 'errorText': "Certains billons ont des valeurs de diamètre inférieures à 30 cm. Impossible dans le PSDRF", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})

  # ----- Contrôle DiamIni et DiamFin non vides pour les billons > 5m :
  temp = BMSsup30[(BMSsup30["DiamFin"].isna() | BMSsup30["DiamMed"].isna() | BMSsup30["DiamIni"].isna()) & (BMSsup30["Longueur"] >= 5)]
  temp = temp[["NumPlac", "Id", "DiamFin", "DiamMed", "DiamIni", "Longueur"]]
  if not temp.empty:
    error_List_Temp=[]
    for index, row in temp.iterrows():
      err = {
          "message": "Il manque une valeur pour le billon  "+ str(int(row["Id"])) +" de la placette "+ str(int(row["NumPlac"])),
          "table": "BMSsup30",
          "column": ["NumPlac", "Id", "DiamFin", "DiamMed", "DiamIni", "Longueur"],
          "row": [index], 
          "value": temp.loc[[index],:].to_json(orient='records'),
        }
      error_List_Temp.append(err)
    verificationList.append({'errorName': "Diamètre(s) manquant(s) dans BMSsup30", 'errorText': "Valeurs manquantes dans 'DiamIni', 'DiamMed' ou 'DiamFin' pour des billons d'au moins 5 m de longueur. Impossible dans le PSDRF", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})

  # ----- Contrôle DiamIni vide ou DiamFin vides pour les billons < 5m :
  temp = BMSsup30[((~BMSsup30["DiamFin"].isna()) | (~BMSsup30["DiamIni"].isna())) & (BMSsup30["Longueur"] < 5)]
  temp = temp[["NumPlac", "Id", "DiamFin", "DiamIni", "Longueur"]]
  if not temp.empty:
    error_List_Temp=[]
    for index, row in temp.iterrows():
      err = {
          "message": "DiamIni et/ou de DiamFin sont renseignées pour le billon  "+ str(int(row["Id"])) +" de la placette "+ str(int(row["NumPlac"])),
          "table": "BMSsup30",
          "column": ["NumPlac", "Id", "DiamFin", "DiamIni", "Longueur"],
          "row": [index], 
          "value": temp.loc[[index],:].to_json(orient='records'),
        }
      error_List_Temp.append(err)
    verificationList.append({'errorName': "Diamètre(s) non necessaire(s) dans BMSsup30", 'errorText': "Billons de moins 5m de longueur pour lesquels des valeurs de 'DiamIni' et/ou de 'DiamFin' sont renseignées (impossible dans le PSDRF)", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})


  # ----- Contrôle DiamIni > DiamMed > DiamFin pour les billons < 5m :
  temp = BMSsup30[~((BMSsup30["DiamIni"] > BMSsup30["DiamMed"]) & (BMSsup30["DiamMed"] > BMSsup30["DiamFin"])) & (BMSsup30["Longueur"] >= 5)]
  temp = temp[["NumPlac", "Id", "DiamFin", "DiamMed", "DiamIni", "Longueur"]]
  if not temp.empty:
    error_List_Temp=[]
    for index, row in temp.iterrows():
      err = {
          "message": "La logique 'DiamIni' > 'DiamMed' > 'DiamFin' n'est pas respectée pour le billon  "+ str(int(row["Id"])) +" de la placette "+ str(int(row["NumPlac"])),
          "table": "BMSsup30",
          "column": ["NumPlac", "Id", "DiamFin", "DiamMed", "DiamIni", "Longueur"],
          "row": [index], 
          "value": temp.loc[[index],:].to_json(orient='records'),
        }
      error_List_Temp.append(err)
    verificationList.append({'errorName': "Grandeurs des Diamètre(s) incohérents dans BMSsup30", 'errorText': "Incohérence possible dans les diamètres des billons : certains ne respectent pas la logique 'DiamIni' > 'DiamMed' > 'DiamFin'", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})

  

  # ---------- Contrôle du suivi des BMsup30 entre les inventaires
  last_cycle = int(BMSsup30["Cycle"].max())
  if last_cycle>1:
    # Contrôle du suivi des arbres dans le temps impossible s'il existe des doublons sur l'association NumDisp-NumPlac-Id (identifiant)
    if df_Dupl.empty:
      t = BMSsup30[["NumDisp", "NumPlac", "Id", "Cycle", "Essence", "Azimut", "Dist"]]
      t = pd.melt(t, id_vars=["NumDisp", "NumPlac", "Id", "Cycle"], value_vars=["Essence", "Azimut", "Dist"], ignore_index=False)
      #On utilise la fonction first car il n'y a pas de duplicate dans notre cas. 
      t = t.pivot_table(index=["NumDisp", "NumPlac", "Id", "variable"], columns='Cycle',values='value', aggfunc=['first', lambda x: x.index[0]]).reset_index()
      t = t.sort_values(by=["NumDisp", "NumPlac", "Id", "variable"])
      # Note : on distingue quand il y a 2 cycles et 1 seul

      # Cas où un arbre présent au cycle 1, disparaît au cycle 2 et réapparaît au cycle3
      if last_cycle > 2:
        pos_Error = []
        df_temp = t[~t.iloc[:,t.shape[1]-1].isna()]
        # Si arbre non coupé au dernier cycle, toutes les valeurs doivent être identiques
        for i in range(5, t.shape[1]):
          pos_Error =  np.concatenate((pos_Error, np.array(np.where(df_temp.iloc[:, i] != df_temp.iloc[:, i-1])).tolist()[0]))
        pos_Error = np.unique(pos_Error)
        df_Error = df_temp.iloc[pos_Error, : ]

      # Cas où on n'a que 2 cycles
      else:
        temp1 = t[(~t.iloc[:,4].isna()) & (~t.iloc[:,5].isna())]
        pos_Error = np.where(temp1.iloc[:,4] != temp1.iloc[:,5])
        pos_Error = np.unique(pos_Error)
        df_Error = temp1.iloc[pos_Error, : ]
      if df_Error.shape[0] >0:
        error_List_Temp = []
        for index, row in df_Error.iterrows():
          tValues = BMSsup30[["NumArbre", "Cycle", str(row["variable"].item())]].loc[[int(x) for x in row["<lambda>"].values]]
          err = {
              "message": "Incohérence(s) relevée(s) sur les valeurs "+ str(row["variable"].item()) +" pour l'id numéro "+ str(row["Id"].item()) + " de la placette numéro " + str(row["NumPlac"].item()),
              "table": "BMSsup30",
              "column": [ "Id", "Cycle", str(row["variable"].item())],
              "row": [int(x) for x in row["<lambda>"].values], 
              "value": tValues.to_json(orient='records'),
            }
          error_List_Temp.append(err)
        verificationList.append({'errorName': "Incohérence(s) dans BMSsup30", 'errorText':  "Incohérence(s) relevée(s) sur les valeurs d'Essence, Azimut et Dist entre les différents inventaires", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})

    # ----- Contrôle Accroissement en diamètre
    if df_Dupl.empty:
      t = BMSsup30[["NumDisp", "NumPlac", "Id", "Cycle", "DiamMed"]]
      t = pd.melt(t, id_vars=["NumDisp", "NumPlac", "Id", "Cycle"], value_vars=["DiamMed"], ignore_index=False)

      #On utilise la fonction first car il n'y a pas de duplicate dans notre cas. 
      t = t.pivot_table(index=["NumDisp", "NumPlac", "Id", "variable"], columns='Cycle',values='value', aggfunc=['first', lambda x: x.index[0]]).reset_index()
      t = t.sort_values(by=["NumDisp", "NumPlac", "Id", "variable"])
    
      if last_cycle > 2:
        #Sous ensemble des arbres non coupés au dernier cycle
        pos_Error = []
        for i in range(5, t.shape[1]):
          pos_Error =  np.concatenate((pos_Error, np.array(np.where(t.iloc[:, i] > t.iloc[:, i-1])).tolist()[0]))
        pos_Error = np.unique(pos_Error)
        df_Error = df_temp.iloc[pos_Error, : ]
      else :
        pos_Error = np.where(~(pd.isnull(t.shape[1])) & ((t.iloc[:, 4]) < (t.iloc[:,5])))
        pos_Error = np.unique(pos_Error)
        df_Error = t.iloc[pos_Error, : ]

      if df_Error.shape[0] > 0 :
        error_List_Temp = []
        for index, row in df_Error.iterrows():
          tValues = BMSsup30[["NumArbre", "Cycle", str(row["variable"].item())]].loc[[int(x) for x in row["<lambda>"].values]]
          err = {
            "message": "Accroissement(s) sur le "+ str(row["variable"].item()) +" positif(s)  pour l'id numéro "+ str(row["Id"].item()) + " de la placette numéro " + str(row["NumPlac"].item()),
            "table": "BMSsup30",
            "column": [ "Id", "Cycle", str(row["variable"].item())],
            "row": [int(x) for x in row["<lambda>"].values], 
            "value": tValues.to_json(orient='records'),
                }
          error_List_Temp.append(err)
        verificationList.append({'errorName': "Accroissement positif dans BMSsup30", 'errorText': "Accroissement(s) sur le diamètre positif(s) constaté(s) entre les différents inventaires.", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})


    # ----- Contrôle sur les écarts de diamètre entre les cycles trop importants
    t = BMSsup30[["NumDisp", "NumPlac", "Id", "Cycle", "DiamMed"]]
    t = pd.melt(t, id_vars=["NumDisp", "NumPlac", "Id", "Cycle"], value_vars=["DiamMed"], ignore_index=False)
    #On utilise la fonction first car il n'y a pas de duplicate dans notre cas. 
    t = t.pivot_table(index=["NumDisp", "NumPlac", "Id", "variable"], columns='Cycle',values='value', aggfunc=['first', lambda x: x.index[0]]).reset_index()
    t = t.sort_values(by=["NumDisp", "NumPlac", "Id", "variable"])
    pos = []
    for i in range(1, last_cycle) :

      t["temp"] = abs(t.iloc[:, i + 4] - t.iloc[: , i +3])
      error_trees = t[t["temp"] > 15]

    if error_trees.shape[0] > 0 :
      error_List_Temp = []
      for index, row in error_trees.iterrows():
        tValues = BMSsup30[["Id", "Cycle", str(row["variable"].item())]].loc[[int(x) for x in row["<lambda>"].values],:]
        err = {
            "message": "Valeur d'accroissement trop importante pour le "+ str(row["variable"].item()) +" de l'arbre id "+ str(row["Id"].item()) + " de la placette numéro " + str(row["NumPlac"].item()),
            "table": "BMSsup30",
            "column": [ "Id", "Cycle", str(row["variable"].item())],
            "row": [int(x) for x in row["<lambda>"].values], 
            "value": tValues.to_json(orient='records'),
          }
      error_List_Temp.append(err)
      verificationList.append({'errorName': "Accroissement anormal dans BMSsup30", 'errorText': "Valeur(s) d'accroissement en diamètre trop importante(s) détectée(s) (seuil à 15 cm entre les 2 inventaires", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})

  ###Table Regeneration
  error_List_Temp = check_species(Regeneration, CodeEssence, Test, "Regeneration")
  if len(error_List_Temp) >0:
    verificationList.append({'errorName': 'Essence dans Regeneration', 'errorText':"Essence dans Regeneration", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})

  # --- Contrôle des Cycles de Regenerations :
  # ----- Contrôle des valeurs vides des variables :
  Vital = Regeneration[ Regeneration["NumPlac"].isna() | Regeneration["SsPlac"].isna() |  Regeneration["Essence"].isna() ]
  Vital = Vital[["NumPlac", "SsPlac", "Essence"]]
  if not Vital.empty:
    error_List_Temp=[]
    for index, row in Vital.iterrows():
      err = {
          "message": "Une/des colonne(s) de la sous placette "+ str(int(row["SsPlac"])) +" de la placette "+ str(int(row["NumPlac"])) + " n'est/ne sont pas renseignées.",
          "table": "Regeneration",
          "column": ["NumPlac", "SsPlac", "Essence"],
          "row": [index], 
          "value": Vital.loc[[index],:].to_json(orient='records'),
        }
      error_List_Temp.append(err)
    verificationList.append({'errorName': "Informations manquantes dans Regeneration", 'errorText': "Il manque des informations à une/des colonne(s) dans la table Regeneration", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})


  # Contrôle des valeurs dupliquées
  error = []
  df_Dupl_temp= Regeneration[["NumDisp", "NumPlac", "Cycle", "SsPlac", "Essence"]].sort_values(by=["NumDisp", "NumPlac", "Cycle", "SsPlac", "Essence"])
  Regeneration= Regeneration.sort_values(by=["NumDisp", "NumPlac", "Cycle", "SsPlac", "Essence"])

  df_Dupl = df_Dupl_temp[df_Dupl_temp.duplicated()]
  if not df_Dupl.empty:
    entire_df_Dupl = df_Dupl_temp[df_Dupl_temp.duplicated(keep=False)]
    listDupl = entire_df_Dupl.groupby(list(df_Dupl_temp)).apply(lambda x: list(x.index)).tolist()
    i = 0
    error_List_Temp = []
    for index, row in df_Dupl.iterrows():
      valuesDupl = entire_df_Dupl.loc[listDupl[i]]
      err = {
          "message": "L'essence" + str(row["Essence"])+ "de la sous placette "+ str(row["SsPlac"])+" de la placette "+ str(int(row["NumPlac"])) +" au cycle "+ str(row["Cycle"]) +" apparaît plusieurs fois dans la table Regeneration",
          "table": "Regeneration",
          "column": ["NumDisp", "NumPlac", "SsPlac", "Cycle", "Essence"],
          "row": listDupl[i], 
          "value": valuesDupl.to_json(orient='records'),
        }
        #possibilité de supression d'un des 2 ou de modification
      i = i + 1
      error_List_Temp.append(err)
    verificationList.append({'errorName': "Duplication dans Regeneration", 'errorText': 'Lignes dupliquées dans la table Regeneration', 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})




  ### Table Transect  
  ##### Contrôle des essences inventoriées dans la table #####
  error_List_Temp = check_species(Transect, CodeEssence, Test, "Transect")
  if len(error_List_Temp) >0:
    verificationList.append({'errorName': 'Essence dans Transect','errorText': 'Essence dans Transect', 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})

  ##### Contrôle des stades de décomposition #####
  error_List_Temp = check_code(CodeDurete, Transect, soundness_code, "Transect")
  if len(error_List_Temp) >0:
    verificationList.append({'errorName': 'Contrôle Stade de décomposition dans Transect','errorText': 'Contrôle Stade de décomposition dans Transect', 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})

  ##### Contrôle des stades de d'écorce #####  
  error_List_Temp = check_code(CodeEcorce, Transect, bark_code, "Transect")
  if len(error_List_Temp) >0:
    verificationList.append({'errorName': 'Contrôle Stade de décomposition dans Transect','errorText': 'Contrôle Stade de décomposition dans Transect', 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})

  ##### Contrôle des Cycles de Transect #####  
  check_cycle_Error_List = check_cycle(Transect, Test, CyclesCodes, "Transect", An, Dispositifs)
  if len(check_cycle_Error_List) >0:
    verificationList.append({'errorName': 'Contrôle cycles dans Transect','errorText': 'Contrôle des cycles dans Transect', 'errorList' : check_cycle_Error_List, 'errorType': 'PsdrfError'})

  # ----- Contrôle des valeurs vides des variables :
  Vital = Transect[ Transect["Id"].isna() |  Transect["Essence"].isna() | Transect["Transect"].isna() |  Transect["Diam"].isna() | Transect["Contact"].isna() |  Transect["Angle"].isna() | Transect["Chablis"].isna() |  Transect["StadeD"].isna() |  Transect["StadeE"].isna() ]
  Vital = Vital[["Id", "Essence", "Transect", "Diam", "Contact", "Angle", "Chablis", "StadeD", "StadeE"]]
  if not Vital.empty:
    error_List_Temp=[]
    for index, row in Vital.iterrows():
      err = {
          "message": "Une/des colonne(s) de la table Transect n'est/ne sont pas renseigné(s)",
          "table": "Transect",
          "column": ["Id", "Essence", "Transect", "Diam", "Contact", "Angle", "Chablis", "StadeD", "StadeE"],
          "row": [index], 
          "value": Vital.loc[[index],:].to_json(orient='records'),
        }
      error_List_Temp.append(err)
    verificationList.append({'errorName': "Informations manquantes dans Transect", 'errorText': "Il manque des informations à une/des colonne(s) dans la table Transect", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})


# ---------- Contrôle des valeurs dupliquées : ---------- #
  df_Dupl_temp= Transect[["NumDisp", "NumPlac", "Id", "Cycle"]].sort_values(by=["NumDisp", "NumPlac", "Id", "Cycle"])
  df_Dupl = df_Dupl_temp[df_Dupl_temp.duplicated()]
  if not df_Dupl.empty:
    entire_df_Dupl = df_Dupl_temp[df_Dupl_temp.duplicated(keep=False)]
    listDupl = entire_df_Dupl.groupby(list(df_Dupl_temp)).apply(lambda x: list(x.index)).tolist()
    i = 0
    error_List_Temp = []
    for index, row in df_Dupl.iterrows():
      valuesDupl = entire_df_Dupl.loc[listDupl[i]]
      err = {
          "message": "L'Id" + str(row["Id"])+ "de la placette "+ str(row["NumPlac"]) +" au cycle "+ str(row["Cycle"]) +" apparaît plusieurs fois dans la table Transect",
          "table": "Transect",
          "column": ["NumDisp", "NumPlac", "Id", "Cycle"],
          "row": listDupl[i], 
          "value": valuesDupl.to_json(orient='records'),
        }
      i = i + 1
      error_List_Temp.append(err)
    verificationList.append({'errorName': "Duplication dans Transect", 'errorText': 'Lignes dupliquées dans la table Transect', 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})



# ---------- Contrôle des valeurs d'angle (≤ 50) : ---------- #
  Transect = Transect.sort_values(by=["NumDisp", "NumPlac", "Id", "Cycle", "Angle"])
  temp = Transect[Transect["Angle"] > 50]
  temp = temp[["NumPlac", "Id", "Angle"]]
  if not temp.empty:
    error_List_Temp=[]
    for index, row in temp.iterrows():
      err = {
          "message": "A l'Id  "+ str(int(row["Id"])) +" de la placette "+ str(int(row["NumPlac"])) + " l'angle mesure plus de 50°.",
          "table": "Transect",
          "column": [ "NumPlac", "Id", "Angle"],
          "row": [index], 
          "value": temp.loc[[index],:].to_json(orient='records'),
        }
      error_List_Temp.append(err)
    verificationList.append({'errorName': "Angle(s) incohérent(s) dans Transect", 'errorText': "Angle faisant strictement plus de  50°. Impossible dans le PSDRF.", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})


  ### Table Placettes
  # Contrôle des valeurs vides des variables 
  Vital = Placettes[ Placettes["Strate"].isna() |  Placettes["PoidsPlacette"].isna()]
  Vital = Vital[["Strate", "PoidsPlacette"]]
  if not Vital.empty:
    error_List_Temp=[]
    for index, row in Vital.iterrows():
      err = {
          "message": "Une/des colonne(s) de la table Placettes n'est/ne sont pas renseignée(s)",
          "table": "Placettes",
          "column": ["Strate", "PoidsPlacette"],
          "row": [index], 
          "value": Vital.loc[[index],:].to_json(orient='records'),
        }
      error_List_Temp.append(err)
    verificationList.append({'errorName': "Informations manquantes dans Placettes", 'errorText': "Il manque des informations à une/des colonne(s) dans la table Placettes", 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})



  # --- Contrôler cohérence NumDisp avec les tables : Arbres, BMSsup30, Regeneration, Transect et Cycles
  def miss2 (table, Placettes, tablename):
    if table.shape[0] >0:
      temp1 = table[["NumDisp", "NumPlac"]]
      temp1 = temp1.drop_duplicates()
      temp1= temp1.assign(Corresp1 = 1)
      temp1['index_col_temp1'] = temp1.index
      temp1["NumDisp"]= temp1["NumDisp"].astype(int)
      temp1["NumPlac"]= temp1["NumPlac"].astype(int)

      temp2 = Placettes[["NumDisp", "NumPlac"]]
      temp2= temp2.assign(Corresp2 = 2)
      temp2['index_col_temp2'] = temp2.index
      temp2["NumDisp"]= temp2["NumDisp"].astype(int)
      temp2["NumPlac"]= temp2["NumPlac"].astype(int)

      temp3 = pd.merge(temp1, temp2, how="outer", on=["NumDisp", "NumPlac"])
      temp3 = temp3[temp3["Corresp1"].isna() | temp3["Corresp2"].isna() ]      

      list1 = temp3[temp3["Corresp1"].isna()]
      list2 = temp3[temp3["Corresp2"].isna()]

      if len(list2) >0:
        error_List_Temp=[]
        for index, row in list2.iterrows():
          err = {
              "message": "La Ligne au numéro de dispositif"+ str(int(row["NumDisp"])) +" et au numéro de placette "+ str(int(row["NumPlac"])) + " figure dans la table " + tablename+" mais ne figure pas dans la table Placette",
              "table": tablename,
              "column": [ "NumDisp", "NumPlac"],
              "row": [int(row["index_col_temp1"])], 
              "value": list2.loc[[index],:].to_json(orient='records'),
            }
          error_List_Temp.append(err)
        verificationList.append({'errorName': "Information incohérente entre la table Placette et la table" +tablename, 'errorText': "Information incohérente entre la table Placette et la table" +tablename, 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})

      if len(list1) >0:
        error_List_Temp=[]
        for index, row in list1.iterrows():
          err = {
              "message": "La Ligne au numéro de dispositif "+ str(int(row["NumDisp"])) +" et au numéro de placette "+ str(int(row["NumPlac"])) + " figure dans la table Placette mais ne figure pas dans la table " + tablename,
              "table": "Placettes",
              "column": [ "NumDisp", "NumPlac"],
              "row": [int(row["index_col_temp2"])],
              "value": list1.loc[[index],:].to_json(orient='records'),
            }
          error_List_Temp.append(err)
        verificationList.append({'errorName': "Information incohérente entre la table Placette et la table" +tablename, 'errorText': "Information incohérente entre la table Placette et la table" +tablename, 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})

  miss2(Arbres, Placettes, "Arbres")
  miss2(BMSsup30, Placettes, "BMSsup30")
  miss2(Cycles, Placettes, "Cycles")
  miss2(Regeneration, Placettes, "Regeneration")
  miss2(Transect, Placettes, "Transect")

  # ---------- Contrôle des valeurs dupliquées : ---------- #
  df_Dupl_temp= Placettes[["NumDisp", "NumPlac", "Cycle", "Strate"]].sort_values(by=["NumDisp", "NumPlac", "Cycle", "Strate"])
  df_Dupl = df_Dupl_temp[df_Dupl_temp.duplicated()]
  if not df_Dupl.empty:
    entire_df_Dupl = df_Dupl_temp[df_Dupl_temp.duplicated(keep=False)]
    listDupl = entire_df_Dupl.groupby(list(df_Dupl_temp)).apply(lambda x: list(x.index)).tolist()
    i = 0
    error_List_Temp = []
    for index, row in df_Dupl.iterrows():
      valuesDupl = entire_df_Dupl.loc[listDupl[i]]
      err = {
          "message": "La placette "+ str(row["NumPlac"]) +" au cycle "+ str(row["Cycle"]) +" à la strate" +  str(row["Strate"])+" apparaît plusieurs fois dans la table Placettes",
          "table": "Placettes",
          "column": ["NumDisp", "NumPlac", "Cycle", "Strate"],
          "row": listDupl[i], 
          "value": valuesDupl.to_json(orient='records'),
        }
      i = i + 1
      error_List_Temp.append(err)
    verificationList.append({'errorName': "Duplication dans Placettes", 'errorText': 'Lignes dupliquées dans la table Placettes', 'errorList': error_List_Temp, 'errorType': 'PsdrfError'})


  # SHAPE



  # TODO: Import des fichiers shape (ligne 4059)






  # Table Cycles des classeurs d'inventaire
  ##### Contrôle des valeurs vides des variables #####
  Vital = Cycles[ Cycles["Coeff"].isna() |  Cycles["Année"].isna() | Cycles["DiamLim"].isna()]
  if not Vital.empty:
    print("Il manque des informations (vides) au(x) colonne(s) dans la table Cycles")

  # ---------- Contrôle des valeurs dupliquées : ---------- #
  Cycles = Cycles[["NumDisp", "NumPlac", "Cycle"]].sort_values(by=["NumDisp", "NumPlac", "Cycle"])
  df_Dupl = Cycles[Cycles.duplicated()]
  if not df_Dupl.empty:
    print("Information dupliquée dans la table")

  def miss3 (table, Placettes, tablename):
      if table.shape[0] >0:
        temp1 = table.drop_duplicates(subset=["NumDisp", "NumPlac", "Cycle"])
        temp1= temp1.assign(Corresp1 = 1)
        temp2 = Placettes[["NumDisp", "NumPlac", "Cycle"]]
        temp2= temp2.assign(Corresp2 = 2)
        temp3 = pd.merge(temp1, temp2, how="outer")
        temp3 = temp3[temp3["Corresp1"].isna() | temp3["Corresp2"].isna() ]

        list1 = temp3[temp3["Corresp1"].isna()]
        list2 = temp3[temp3["Corresp2"].isna()]

        if len(list2) >0:
          print("Un des numéros d'inventaires figure dans la table" + tablename+ "mais ne figure pas dans la table Placette")
        
        if len(list1) >0:
          print("Un des numéros d'inventaires figure dans la table Placette mais ne figure pas dans la table Placette"+ tablename)



  # Table Reperes
  if Reperes.shape[0]>0:
  # ---------- Contrôle des valeurs dupliquées : ---------- #
    Reperes = Reperes.sort_values(by=["NumDisp", "NumPlac", "Azimut", "Dist"])
    df_Dupl = Reperes[Reperes.duplicated()]
    if not df_Dupl.empty:
      print("Information dupliquée dans la table")


  # Conformité avec les codifications
  # CodeDureté

  # Harmonisation avec le document administrateur
  # --- Contrôle des NumDisp de Dispositifs :
  df = Dispositifs[Dispositifs["NumDisp"]==disp_num]
  if df.empty:
    print("Impossible de retrouver le dispositif dans la table dispositif")

  # ----- Contrôle des valeurs vides des variables :
  Vital = Dispositifs[ Dispositifs["Statut1"].isna()]
  if not Vital.empty:
    print("Il manque des informations (vides) au(x) colonne(s) dans la table Dispositifs")

  ##### Contrôle des valeurs dupliquées #####
  Dispositifs = Dispositifs.sort_values(by=["NumDisp", "Nom"])
  df_Dupl = Dispositifs[Dispositifs.duplicated()]
  if not df_Dupl.empty:
    print("Information dupliquée dans la table Dispositifs")


  #Table EssReg
  df = EssReg[EssReg["NumDisp"] ==disp_num]
  if not df.empty: 
    print("Des regroupements d'essence ont été renseignés pour ce dispositif")


  #Contrôle sur les essences inventoriées dans la table
  # error_List_Temp = check_species(Arbres, CodeEssence, Test, "Arbres")
  # if len(error_List_Temp) >0:
  #   verificationList.append({'errorName': 'Essence dans Arbres', 'errorList': error_List_Temp, 'correctionList': CodeEssence['Essence'].tolist()})

  # Contrôle de la cohérence avec les tables d'inventaire
  #Principe : toutes les essences rencontrées dans l'inventaire doivent figurer dans la table EssReg
  error_List_Temp = check_species(Arbres, EssReg, Test, "Arbres")
  # if len(error_List_Temp) >0:
    # verificationList.append({'errorName': 'Essence Reg dans Arbres', 'errorList': error_List_Temp, 'correctionList': EssReg['Essence'].tolist()})

  error_List_Temp = check_species(Regeneration, EssReg, Test, "Regeneration")
  # if len(error_List_Temp) >0:
    # verificationList.append({'errorName': 'Essence Reg dans Regeneration', 'errorList': error_List_Temp, 'correctionList': EssReg['Essence'].tolist()})

  error_List_Temp = check_species(Transect, EssReg, Test, "Transect")
  # if len(error_List_Temp) >0:
    # verificationList.append({'errorName': 'Essence Reg dans Transect', 'errorList': error_List_Temp, 'correctionList': EssReg['Essence'].tolist()})

  error_List_Temp = check_species(BMSsup30, EssReg, Test, "BMSsup30")
  # if len(error_List_Temp) >0:
    # verificationList.append({'errorName': 'Essence Reg dans BMSsup30', 'errorList': error_List_Temp, 'correctionList': EssReg['Essence'].tolist()})

  error_List_Temp = check_species(Tarifs, EssReg, Test, "Tarifs")
  # if len(error_List_Temp) >0:
    # verificationList.append({'errorName': 'Essence Reg dans Tarifs', 'errorList': error_List_Temp, 'correctionList': EssReg['Essence'].tolist()})

  
  #Table Referents



  # TODO: Travail sur colonnes Annexes (remarques)

  # #Contrôle des stades de décomposition
  # error_List_Temp = check_code(CodeDurete, Arbres, soundness_code, "Arbres")
  # if len(error_List_Temp) >0:
  #   verificationList.append({'errorName': 'Contrôle Stade dans Arbres', 'errorList': error_List_Temp, 'correctionList': CodeDurete['Code'].tolist()})
  verifiedObj = {"verificationObj": verificationList, "correctionList": correctionList}

  verifiedJson = json.dumps(verifiedObj, cls=NumpyEncoder)


  #Contrôle des stades d'écorce



  # error_List_Temp = check_species("BMSsup30", "CodeEssence", Test, "BMSsup30")
  # if len(error_List_Temp) >0:
  #   verificationList.append({'errorName': 'Essence dans BMSsup30', 'errorList': error_List_Temp, 'correctionList': CodeEssence['Essence'].tolist()})
  # check_species_Error_List = check_species(BMSsup30, CodeEssence, Test, "BMSsup30")
  # if len(check_species_Error_List) >0:
  #   verificationList.append({'errorName': 'Essence dans BMSsup30', 'errorList': check_species_Error_List, 'correctionList': CodeEssence['Essence'].tolist()})




  return verifiedJson

# Fonction d'encodage en Json
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def check_null_DPC (table, tablename):
  ListName = table.columns[table.isna().any()]
  if ListName.size > 0:
    Vital = ListName[pd.Series(ListName).isin(["NumDisp", "NumPlac", "Cycle"])]
    # Annexe = ListName[~ListName.isin(["NumDisp", "NumPlac", "Id", "Cycle", "Essence", "DiamMed", "Longueur", "StadeD", "StadeE", "Observation"])]
    if Vital.size > 0:
      print("Il manque des informations (vides) au(x) colonne(s) dans la table" + tablename)
  # Vital = table[table["NumDisp"].isna() | table["NumPlac"].isna() | table["Cycle"].isna()]
  # if not Vital.empty:
  #   print("Il manque des informations (vides) au(x) colonne(s) dans la table" + tablename)


##### fonction pour filtrer les tables selon une liste de dispositifs #####
def filter_by_disp(disp_list, cycle, table, disp_num) :
  num_list = disp_num
  # for tmp in tables:
  #     tmp_NAME = tmp
  #     tmp = tableDict[tmp]
      
  if isinstance(table, pd.DataFrame):
      if table.shape[0] > 0:
          table = table[table['NumDisp']==num_list ]
          
          # -- filtre selon le cycle
          if "Cycle" in table.columns:
              table = table[table['Cycle'] <= cycle]
              
          if cycle == 1 : 
              table = table.assign(AcctGper = None, 
                              AcctVper = None, 
                              AcctD = None)
  return table 

# fonction contrôle des essences rencontrées
def check_species(table_to_test, species, status, tablename):
  error = []
  # Récupérer les essences qui apparaissent dans table_to_test mais pas dans species
  species_list_temp = table_to_test[(~table_to_test['Essence'].isin(species['Essence'])) & (~table_to_test['Essence'].isna())]\
  [['Essence']]
  species_list = species_list_temp.drop_duplicates()['Essence'].tolist()

  if len(species_list) > 0:
      status = np.where(status >= 2, status, 2)
      for index, row in species_list_temp.iterrows():
          err= {
            "message": "L'essence "+ str(row["Essence"]) + " figure dans la table "+ tablename +"mais ne figure pas dans la table 'CodeEssence' (fichier administrateur) ",
            "table": tablename,
            "column": ['Essence'],
            "row": [index],
            "value": species_list_temp.loc[[index],:].to_json(orient='records'),
          }
          error.append(err)
  return error



##### fonction contrôle des Cycles ####
def check_cycle(table_to_test, status, cycle_admin, tablename, An, Dispositifs): 
    if table_to_test.shape[0] > 0 :
      error = []
      temp = table_to_test.assign(Mark = 1) # add marker

      cycle_table =  pd.merge(cycle_admin, temp[["NumDisp", "Cycle", "Mark"]], how='outer').drop_duplicates()
      
      # test si éléments de la table sont absents de la table Cycle (avec DateIni est bien inférieur à l'année en cours 'An')
      pos = np.array(np.where((cycle_table['Mark'].isna()) & (cycle_table['DateIni'] < An))).tolist()[0]

      if len(pos)>0:
        if status >= 2:
            status = status
        else:
            status = 2
            
        # liste des tuples NumDisp + Cycle qui ne figurent pas dans la table testée
        vecttemp = cycle_table.loc[pos,["NumDisp", "Cycle"]].drop_duplicates()
        
        for index, row in vecttemp.iterrows() :
          nomDisp =  Dispositifs[Dispositifs["NumDisp"]==row["NumDisp"]]["Nom"].item()
          err = {
            "message": "La table Cycles du fichier administrateur contient le cycle "+ str(row['Cycle']) + " pour le dispositif " + str(row['NumDisp'])+ "-"+ nomDisp + ", mais ce dernier n'apparaît pas dans la table" + tablename +".",
            "table": tablename,
            "column": 'Cycle',
          }
          error.append(err)

    else:
        status = 1
        label = "La feuille"+ tablename +" ne contient pas de données."
    
    return error


##### fonction contrôle des stades écorce et de décomposition #####
def check_code(code_admin, table_to_test, code_to_check, tableName):
  error = []

  if code_to_check == "écorce":
      stade = "StadeE"
  else:
      stade= "StadeD"

  column =["NumDisp", "NumPlac", "Id", "Cycle", stade]

  # détection des codes non conformes
  table_to_test=table_to_test[table_to_test[stade].notna()]
  print(table_to_test)
  print(code_admin['Code'].values)
  df1 = table_to_test[~table_to_test[stade].isin( code_admin['Code'].values)]
  print(table_to_test[stade].isin( code_admin['Code'].values))
  print(code_admin['Code'].values.dtype)
  print(table_to_test.dtypes)
  print(df1)

  df = df1.loc[:,df1.columns.isin([stade])].drop_duplicates()

  if df.shape[0]>0:
    for index, row in df.iterrows():
      err= {
        "message": "Stade(s) "+code_to_check+" "+ str(int(row[stade]))  +" non conforme(s) dans la table" +tableName,
        "table": tableName,
        "column": [stade],
        "row": [index],
        "value": df.loc[[index],:].to_json(orient='records'),
      }
      error.append(err)


  return(error)


# table_to_test=Transect[Transect["StadeD"].notna()]
# table_to_test
# df1 = table_to_test[~table_to_test["StadeD"].isin( CodeDurete['Code'].values)]
# df1
# df = df1.loc[:,df1.columns.isin(["StadeD"])].drop_duplicates()
# df




##### fonction contrôle des stades écorce et de décomposition #####



##### fonction pour filtrer les tables selon une liste de dispositifs #####



##### fonction pour tester si résultats par placettes vides #####



##### fonction pour tester si coordonnées placettes vides #####



##### fonction de vérification du sf #####
# contrôle : 1/ présence des colonnes NumDisp et NumPlac
#            2/ valeurs vides dans les colonnes NumDisp et NumPlac
#            3/ coordonnées vides ?



##### fonction choix du shape des placettes #####



# -- construction table Arbres

