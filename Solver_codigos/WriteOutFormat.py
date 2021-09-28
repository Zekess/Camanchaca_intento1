import xlsxwriter
import sys
import base64


def xldownload(excel, name):
    data = open(excel, 'rb').read()
    b64 = base64.b64encode(data).decode('UTF-8')
    #b64 = base64.b64encode(xl.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/xls;base64,{b64}" download={name}>Download {name}</a>'
    return href

def write_excel_with_column_size(df,sheetname,writer):
    df.to_excel(writer, sheet_name=sheetname)  # send df to writer
    worksheet = writer.sheets[sheetname]  # pull worksheet object
    for idx, col in enumerate(df):  # loop through all columns
        series = df[col]
        max_len = max((
            series.astype(str).map(len).max(),  # len of largest item
            len(str(series.name))  # len of column name/header
            )) + 4  # adding a little extra space
        worksheet.set_column(idx, idx, max_len)  # set column width
#        print(col,idx,max_len)
    worksheet.set_column(idx+1, idx + 1, max_len)  # set column width
    worksheet.set_column(0, 0, 15)  # set column width
    #writer.save()

# def get_col_widths(dataframe):
#     # First we find the maximum length of the index column   
#     idx_max = max([len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
#     # Then, we concatenate this to the max of the lengths of column name and its values for each column, left to right
#     return [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [len(col)]) for col in dataframe.columns]

def get_col_widths(dict):
    # First we find the maximum length of the index column   
    # idx_max = max([len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
    # Then, we concatenate this to the max of the lengths of column name and its values for each column, left to right
    return [max([len(str(s)) for s in dict[col]] + [len(col)]) for col in dict.keys()]

def get_col_widths(list):
    # First we find the maximum length of the index column   
    # idx_max = max([len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
    # Then, we concatenate this to the max of the lengths of column name and its values for each column, left to right
    return [max([len(str(s)) for s in dict[col]] + [len(elem)]) for elem in list]

def write_violation(row,col,worksheet,text_wrap,bold,weeklySolutions,Eventuales,violation,name):
    #Detalle de cada violación
    if sum([getattr(solution, violation)[worker] 
            for solution in weeklySolutions 
                for worker in getattr(solution, violation).keys()]) > 0:
        for i,solution in enumerate(weeklySolutions):
            worksheet.write(row , col+i+1, "Semana "+str(i+1),bold)

        worksheet.write(row , col+0, name, text_wrap)
        worksheet.set_row(row, 40)
        total_lines = 0
        for week,solution in enumerate(weeklySolutions):
            worker_line = 0
            for worker in getattr(solution, violation).keys():
                if worker in Eventuales:
                    continue
                worker_line += 1
                worksheet.write(row+worker_line, col+0, worker,bold)
                if getattr(solution, violation)[worker] > 0:
                    worksheet.write(row+worker_line, col+1 + week, str(getattr(solution, violation)[worker]))
                if worker_line > total_lines:
                    total_lines = worker_line
        row += 2 + total_lines

    return row

def write_monthly_schedule(weeklySolutions,dias_semana,worksheet,bold):
    #WRITE SOLUTION SCHEDULE
    row = 0
    for i, solution in enumerate(weeklySolutions):
        worksheet.write(row , 0, "Semana "+str(i+1))
        worksheet.write_row(row, 1, dias_semana[i],bold)
        row += 1        
        for key in solution.schedule.keys():
            worksheet.write(row, 0, key, bold)
            worksheet.write_row(row, 1, solution.schedule[key])
            row += 1        
        row += 1

    #SET COLUMN WIDTH
    widths = dict()
    for i, solution in enumerate(weeklySolutions):
        for j, dias in enumerate(dias_semana[i]):
            widths.setdefault(j+1,[]).append(len(str(dias)) + 2) 
        for key in solution.schedule.keys():
            widths.setdefault(0,[]).append(len(str(key)) + 2) 
            for j,dias in enumerate(solution.schedule[key]):
                widths.setdefault(j+1,[]).append(len(str(dias)) + 2) 

    max_width = dict()
    for key in widths.keys():
        max_width[key] = max(widths[key])

    for key in max_width.keys():
        worksheet.set_column(key, key, max_width[key])

    return row

def write_otros(row,col,worksheet,weeklySolutions,text_wrap,bold,Eventuales,conteo,name):
    worksheet.write(row , col+0, name, text_wrap)
    worksheet.set_row(row, 30)
    cantidad_por_persona = dict()
    for solution in weeklySolutions:
        for worker in getattr(solution, conteo).keys():
            cantidad_por_persona.setdefault(worker,[]).append(getattr(solution, conteo)[worker])

    worksheet.write(row,col+1,"Cantidad",bold)
    row += 1
    for worker in cantidad_por_persona.keys():
        if worker in Eventuales:
            continue
        worksheet.write(row,col,worker,bold)
        worksheet.write(row,col+1,sum(cantidad_por_persona[worker]))
        row += 1

    row +=1
    return row

def write_monthly_violations(row,col,worksheet,weeklySolutions,text_wrap,bold,Eventuales):

    #Costos
    bold_wrap = bold
    bold_wrap.set_text_wrap()
    worksheet.write(row, col+1 ,"Cuantificable",bold_wrap)
    worksheet.write(row, col+2 ,"Interno",bold_wrap)
    worksheet.write(row, col+3 ,"Total",bold_wrap)
    row += 1
    worksheet.write(row, col+0 ,"Costo mensual",bold_wrap)

    costo_cuanti_mensual  = sum([solution.scoreCuantificable for solution in weeklySolutions])
    costo_interno_mensual = sum([solution.scoreInterno for solution in weeklySolutions])
    costo_mensual = sum([solution.score for solution in weeklySolutions])
    worksheet.write(row,col+1,costo_cuanti_mensual)
    worksheet.write(row,col+2,costo_interno_mensual)
    worksheet.write(row,col+3,costo_mensual)
    row += 2

    #Número de violaciones
    worksheet.write(row, col+1 ,"Obligatorias",bold_wrap)
    worksheet.write(row, col+2 ,"Otras",bold_wrap)
    row += 1
    worksheet.write(row, col+0 ,"Número de violaciones",bold_wrap)
    worksheet.set_row(row, 30)

    dias_sobra_gente = 0
    for solution in weeklySolutions:
        for dia in solution.requirementViolationsSobran.keys():
            if solution.requirementViolationsSobran[dia] > 0:
                dias_sobra_gente += solution.requirementViolationsSobran[dia]

    violaciones_fuertes = sum([solution.softViolations for solution in weeklySolutions]) - dias_sobra_gente
    violaciones_debiles = sum([solution.hardViolations for solution in weeklySolutions])

    worksheet.write(row, col+1 ,violaciones_fuertes)
    worksheet.write(row, col+2 ,violaciones_debiles)
    row += 2

    piv_col = col
    #Horas Contrato trabajadas
    write_otros(row,col,worksheet,weeklySolutions,text_wrap,bold,Eventuales,
                            'HorasContratoSemanales',"Horas Contrato")
    col += 2
    #Horas Extra trabajadas
    write_otros(row,col,worksheet,weeklySolutions,text_wrap,bold,Eventuales,
                            'HorasExtraSemanales',"Horas Extra")
    col += 2
    #Horas Totales trabajadas
    write_otros(row,col,worksheet,weeklySolutions,text_wrap,bold,Eventuales,
                            'TotalHorasTrabajadas',"Total Horas")
    col += 2
    #Domingos trabajados
    row = write_otros(row,col,worksheet,weeklySolutions,text_wrap,bold,Eventuales,
                            'DomingoTrabajado',"Domingos trabajados")

    col = piv_col
    #Requirement
    row = write_violation(row,col,worksheet,text_wrap,bold,weeklySolutions,Eventuales,
                            'requirementViolationsFaltan',"Falta de trabajadores")
    row = write_violation(row,col,worksheet,text_wrap,bold,weeklySolutions,Eventuales,
                            'requirementViolationsSobran',"Exceso de trabajadores")

    #Gente contratada
    row = write_violation(row,col,worksheet,text_wrap,bold,weeklySolutions,Eventuales,
                            'ViolacionContratadosPorDia',"Contratados en el turno")

    #Max consecutive shifts
    row = write_violation(row,col,worksheet,text_wrap,bold,weeklySolutions,Eventuales,
                            'maxConsecutiveShiftsViolations',"Máximo de turnos consecutivos")
    #Max Shift
    row = write_violation(row,col,worksheet,text_wrap,bold,weeklySolutions,Eventuales,
                            'maxShiftsViolations',"Mantener turnos")
    #Min hours
    row = write_violation(row,col,worksheet,text_wrap,bold,weeklySolutions,Eventuales,
                            'minTotalMinutesViolations',"Mínimo de horas trabajadas")
    #Max hours
    row = write_violation(row,col,worksheet,text_wrap,bold,weeklySolutions,Eventuales,
                            'maxTotalMinutesViolations',"Horas extras")
    #Days Off
    row = write_violation(row,col,worksheet,text_wrap,bold,weeklySolutions,Eventuales,
                            'daysOffViolations',"Domingo o lunes de descanso")

    return None

def write_total_schedule_per_month(row,worksheet,weeklySolutions,dias,bold):
    # Some data we want to write to the worksheet.
    for solution in weeklySolutions:
        IdTurnos = [turnos for turnos in solution.IdTurnos]
        break
    NroTurnos = len(IdTurnos)
    Requirement = max([solution.Requerimientos for solution in weeklySolutions])
    # Workers = set([key for solution in weeklySolutions for key in solution.schedule.keys()])

    GlobalPlanification = dict()
    for solution in weeklySolutions:
        for staffId, schedule in solution.schedule.items():
            for item in schedule:
                GlobalPlanification.setdefault(staffId,[]).append(item)
            if len(schedule) < 7:
                for i in range(0,7-len(schedule)):
                    GlobalPlanification.setdefault(staffId,[]).append(' ')


    calendar = [{} for i in range(0,NroTurnos)]
    tot_dias = [dia for i in dias for dia in i]

    for i,day in enumerate(tot_dias):
        worksheet.write(row+(i)*Requirement+1,0,day,bold)

    # print(GlobalPlanification)
    for key in GlobalPlanification.keys():
        for day, nombre in enumerate(tot_dias):
            for i in range(NroTurnos):
                if GlobalPlanification[key][day].strip() == IdTurnos[i]:
                    calendar[i].setdefault(day,[]).append(key)
                    
    for turno in range(NroTurnos):
        for day in sorted(calendar[turno]):
            for i,worker in enumerate(calendar[turno][day]):
                worksheet.write(row+(day)*Requirement+1+i,2+turno,worker)

    row += (day)*Requirement+1+i
    return row

def WriteOutFormat(output_name, df1, df, prm, weeklySolution):
    import pandas as pd
    import datetime

    writer = pd.ExcelWriter(output_name, engine = 'xlsxwriter')
    #Opciones básicas
    write_excel_with_column_size(df1,'Solución',writer)

    workbook = writer.book
    worksheet1 = workbook.add_worksheet("Calendario")
    bold = workbook.add_format({'bold': True})
    text_wrap = workbook.add_format()
    text_wrap.set_text_wrap()

    #Columnas calendario Global
    NroTurnos = min(len(pd.unique(df.values.ravel('K')))-1,3)
    for i in range(NroTurnos):
        worksheet1.write(0,i+2,"Turno "+str(i+1),bold)

    nro_a_mes = {1:'Enero',2:'Febrero',3:'Marzo',4:'Abril',5:'Mayo',6:'Junio',7:'Julio',
            8:'Agosto',9:'Septiembre',10:'Octubre',11:'Noviembre',12:'Diciembre'}

    #Escritura mes a mes
    weekspermonth = dict()
    dias_semana = dict()
    nombres_semana = list(df.columns.values)
    fecha = prm.dia_inicio
    for week in range(0,prm.NumberOfWeeks):
        if fecha.year%prm.dia_inicio.year == 0:
            weekspermonth.setdefault(fecha.month,[]).append(week)
        else:
            weekspermonth.setdefault(str(fecha.year)+'-'+str(fecha.month),[]).append(week)
            nro_a_mes[str(fecha.year)+'-'+str(fecha.month)]=nro_a_mes[fecha.month]+'-'+str(fecha.year)
        dias_semana[week] = nombres_semana[week*7:(week+1)*7]
        fecha += datetime.timedelta(weeks=1)

    col = 0
    tot_sche_row = 0
    for month in weekspermonth.keys():
        tmp_worksheet = workbook.add_worksheet(nro_a_mes[month])
        month_solutions = [weeklySolution[i] for i in weekspermonth[month]]
        month_days = [dias_semana[i] for i in weekspermonth[month]]
        #write monthly solution
        next_row = write_monthly_schedule(month_solutions,month_days,
                                            tmp_worksheet,bold)

        #write monthly violations and costs
        write_monthly_violations(next_row,col,tmp_worksheet,month_solutions,text_wrap,bold,prm.IdStaffEventual)

        # write_total_schedule
        tot_sche_row = write_total_schedule_per_month(tot_sche_row,worksheet1,month_solutions,month_days,bold)


    #Write complete year
    dias_semana = dict()
    nombres_semana = list(df.columns.values)
    fecha = prm.dia_inicio
    for week in range(0,prm.NumberOfWeeks):
        dias_semana[week] = nombres_semana[week*7:(week+1)*7]
        fecha += datetime.timedelta(weeks=1)
    solutions = [weeklySolution[i] for i in weeklySolution.keys()]
    dias = [dias_semana[i] for i in weeklySolution.keys()]


    #Write total violations plus costs plus dias trabajados
    next_row = 0
    col = 6
    write_monthly_violations(next_row,col,worksheet1,solutions,text_wrap,bold,prm.IdStaffEventual)
    worksheet1.set_column(0,0,15)
    worksheet1.set_column(1,1,3)
    for i in range(0,8):
        worksheet1.set_column(6+i,6+i,15)
    for i in range(0,3):
        worksheet1.set_column(2+i,2+i,13)
    
    workbook.close()
    return output_name, writer
    #writer.save()
    #writer.close()

def OLDWriteOutFormat(output_name, df1, df, prm, weeklySolution):
    import pandas as pd

    writer = pd.ExcelWriter(output_name, engine = 'xlsxwriter')
    #Opciones basicas
    write_excel_with_column_size(df1,'opcion1',writer)

    #Opcion avanzada
    workbook = writer.book
    worksheet1 = workbook.add_worksheet("opcion2")

    #Write Text
    # Add a bold format to use to highlight cells.
    bold = workbook.add_format({'bold': True})
    background = workbook.add_format()
    background.set_pattern(1)
    background.set_bg_color('green')

    worksheet1.set_column(0, 0 , 15)  # set column width
    for i in range(0,prm.ShiftsPerDay):
        worksheet1.write(0,2+i,prm.IdShifts[i],bold)
        worksheet1.set_column(2+i, 2+i, 15)  # set column width

    for i,day in enumerate(df.columns):
        worksheet1.write((i)*prm.Requirement+1,0,day,bold)

    # Some data we want to write to the worksheet.
    calendar = [{} for i in range(0,prm.ShiftsPerDay)]
    for index, worker in df.iterrows():
        for day in range(0,len(df.columns)):
            for i in range(0,prm.ShiftsPerDay):
                if worker[day].strip() == prm.IdShifts[i]:
                    calendar[i].setdefault(day,[]).append(index)

    worksheet2 = writer.sheets['opcion1']  # pull worksheet object
    for turno in range(0,prm.ShiftsPerDay):
        for day in sorted(calendar[turno]):
            for i,worker in enumerate(calendar[turno][day]):
                if i >= prm.Requirement:
                    break
                if (day+1)%7!=0:
                    worksheet1.write((day)*prm.Requirement+1+i,2+turno,worker)
                else:
                    worksheet1.write((day)*prm.Requirement+1+i,2+turno,worker,background)

                line = (day)*prm.Requirement+1+i


    line = 0
    #Costo
    worksheet1.write(line , 6, "Costo Total")
    worksheet1.write(line , 7, sum([weeklySolution[week].score for week in range(0,prm.NumberOfWeeks)]))
    #Violaciones
    line += 2
    if sum([weeklySolution[week].hardViolations for week in range(0,prm.NumberOfWeeks)]) + sum([weeklySolution[week].softViolations for week in range(0,prm.NumberOfWeeks)])> 0:
        worksheet1.write(line , 6, "Violaciones totales")
        worksheet1.write(line , 7, sum([weeklySolution[week].hardViolations for week in range(0,prm.NumberOfWeeks)])+
                                    sum([weeklySolution[week].softViolations for week in range(0,prm.NumberOfWeeks)]))
        line += 2

    import datetime
    for week in range(0,prm.NumberOfWeeks):
        semana = prm.dia_inicio+datetime.timedelta(weeks=week)
        worksheet1.write(line , 8+week, "Semana del "+str(semana.day)+"-"+str(semana.month))
    line += 1

    if sum([weeklySolution[week].minConsecutiveShiftsViolations[worker] for week in range(0,prm.NumberOfWeeks) for worker in weeklySolution[week].minConsecutiveShiftsViolations.keys()]) > 0:
        worksheet1.write(line , 6, "Violación mínimo de turnos consecutivos")
        total_lines = 0
        for week in range(0,prm.NumberOfWeeks):
            worker_line = 0
            for worker in weeklySolution[week].minConsecutiveShiftsViolations.keys():
                worker_line += 1
                if weeklySolution[week].minConsecutiveShiftsViolations[worker] > 0:
                    worksheet1.write(line+worker_line , 7, worker)
                    worksheet1.write(line+worker_line , 8+week, str(weeklySolution[week].minConsecutiveShiftsViolations[worker]))
                    if worker_line > total_lines:
                        total_lines = worker_line
        line += 1 + total_lines

    if sum([weeklySolution[week].maxConsecutiveShiftsViolations[worker] for week in range(0,prm.NumberOfWeeks) for worker in weeklySolution[week].maxConsecutiveShiftsViolations.keys()]) > 0:
        worksheet1.write(line , 6, "Violación máximo de turnos consecutivos")
        total_lines = 0
        for week in range(0,prm.NumberOfWeeks):
            worker_line = 0
            for worker in weeklySolution[week].maxConsecutiveShiftsViolations.keys():
                worker_line += 1
                if weeklySolution[week].maxConsecutiveShiftsViolations[worker] > 0:
                    worksheet1.write(line+worker_line , 7, worker)
                    worksheet1.write(line+worker_line , 8+week, str(weeklySolution[week].maxConsecutiveShiftsViolations[worker]))
                    if worker_line > total_lines:
                        total_lines = worker_line
        line += 1 + total_lines
    
    if sum([weeklySolution[week].minConsecutiveDaysOffViolations[worker] for week in range(0,prm.NumberOfWeeks) for worker in weeklySolution[week].minConsecutiveDaysOffViolations.keys()]) > 0:
        worksheet1.write(line , 6, "Violación mínimo de dias consecutivos no trabajados")
        total_lines = 0
        for week in range(0,prm.NumberOfWeeks):
            worker_line = 0
            for worker in weeklySolution[week].minConsecutiveDaysOffViolations.keys():
                worker_line += 1
                if weeklySolution[week].minConsecutiveDaysOffViolations[worker] > 0:
                    worksheet1.write(line+worker_line , 7, worker)
                    worksheet1.write(line+worker_line , 8+week, str(weeklySolution[week].minConsecutiveDaysOffViolations[worker]))
                    if worker_line > total_lines:
                        total_lines = worker_line
        line += 1 + total_lines
    
    if sum([weeklySolution[week].weekendsViolations[worker] for week in range(0,prm.NumberOfWeeks) for worker in weeklySolution[week].weekendsViolations.keys()]) > 0:
        worksheet1.write(line , 6, "Violación de fin de semanas trabajados")
        total_lines = 0
        for week in range(0,prm.NumberOfWeeks):
            worker_line = 0
            for worker in weeklySolution[week].weekendsViolations.keys():
                worker_line += 1
                if weeklySolution[week].weekendsViolations[worker] > 0:
                    worksheet1.write(line+worker_line , 7, worker)
                    worksheet1.write(line+worker_line , 8+week, str(weeklySolution[week].weekendsViolations[worker]))
                    if worker_line > total_lines:
                        total_lines = worker_line
        line += 1 + total_lines

    if sum([weeklySolution[week].maxShiftsViolations[worker] for week in range(0,prm.NumberOfWeeks) for worker in weeklySolution[week].maxShiftsViolations.keys()]) > 0:
        worksheet1.write(line , 6, "Violación turnos mantenidos durante la semana")
        total_lines = 0
        for week in range(0,prm.NumberOfWeeks):
            worker_line = 0
            for worker in weeklySolution[week].maxShiftsViolations.keys():
                worker_line += 1
                if weeklySolution[week].maxShiftsViolations[worker] > 0:
                    worksheet1.write(line+worker_line , 7, worker)
                    worksheet1.write(line+worker_line , 8+week, str(weeklySolution[week].maxShiftsViolations[worker]))
                    if worker_line > total_lines:
                        total_lines = worker_line
        line += 1 + total_lines

    if sum([weeklySolution[week].maxTotalMinutesViolations[worker] for week in range(0,prm.NumberOfWeeks) for worker in weeklySolution[week].maxTotalMinutesViolations.keys()]) > 0:
        worksheet1.write(line , 6, "Violación horas extras")
        total_lines = 0
        for week in range(0,prm.NumberOfWeeks):
            worker_line = 0
            for worker in weeklySolution[week].maxTotalMinutesViolations.keys():
                worker_line += 1
                if weeklySolution[week].maxTotalMinutesViolations[worker] > 0:
                    worksheet1.write(line+worker_line , 7, worker)
                    worksheet1.write(line+worker_line , 8+week, str(weeklySolution[week].maxTotalMinutesViolations[worker]))
                    if worker_line > total_lines:
                        total_lines = worker_line
        line += 1 + total_lines

    if sum([weeklySolution[week].minTotalMinutesViolations[worker] for week in range(0,prm.NumberOfWeeks) for worker in weeklySolution[week].minTotalMinutesViolations.keys()]) > 0:
        worksheet1.write(line , 6, "Violación mínimo de horas trabajadas")
        total_lines = 0
        for week in range(0,prm.NumberOfWeeks):
            worker_line = 0
            for worker in weeklySolution[week].minTotalMinutesViolations.keys():
                worker_line += 1
                if weeklySolution[week].minTotalMinutesViolations[worker] > 0:
                    worksheet1.write(line+worker_line , 7, worker)
                    worksheet1.write(line+worker_line , 8+week, str(weeklySolution[week].minTotalMinutesViolations[worker]))
                    if worker_line > total_lines:
                        total_lines = worker_line
        line += 1 + total_lines

    if sum([weeklySolution[week].daysOffViolations[worker] for week in range(0,prm.NumberOfWeeks) for worker in weeklySolution[week].daysOffViolations.keys()]) > 0:
        worksheet1.write(line , 6, "Violación días libres")
        total_lines = 0
        for week in range(0,prm.NumberOfWeeks):
            worker_line = 0
            for worker in weeklySolution[week].daysOffViolations.keys():
                worker_line += 1
                if weeklySolution[week].daysOffViolations[worker] > 0:
                    worksheet1.write(line+worker_line , 7, worker)
                    worksheet1.write(line+worker_line , 8+week, str(weeklySolution[week].daysOffViolations[worker]))
                    if worker_line > total_lines:
                        total_lines = worker_line
        line += 1 + total_lines

    if sum([weeklySolution[week].onRequestViolations[worker] for week in range(0,prm.NumberOfWeeks) for worker in weeklySolution[week].onRequestViolations.keys()]) > 0:
        worksheet1.write(line , 6, "Violación solicitación de días a trabajar")
        total_lines = 0
        for week in range(0,prm.NumberOfWeeks):
            worker_line = 0
            for worker in weeklySolution[week].onRequestViolations.keys():
                worker_line += 1
                if weeklySolution[week].onRequestViolations[worker] > 0:
                    worksheet1.write(line+worker_line , 7, worker)
                    worksheet1.write(line+worker_line , 8+week, str(weeklySolution[week].onRequestViolations[worker]))
                    if worker_line > total_lines:
                        total_lines = worker_line
        line += 1 + total_lines

    if sum([weeklySolution[week].offRequestViolations[worker] for week in range(0,prm.NumberOfWeeks) for worker in weeklySolution[week].offRequestViolations.keys()]) > 0:
        worksheet1.write(line , 6, "Violación de solicitación de días a descansar")
        total_lines = 0
        for week in range(0,prm.NumberOfWeeks):
            worker_line = 0
            for worker in weeklySolution[week].offRequestViolations.keys():
                worker_line += 1
                if weeklySolution[week].offRequestViolations[worker] > 0:
                    worksheet1.write(line+worker_line , 7, worker)
                    worksheet1.write(line+worker_line , 8+week, str(weeklySolution[week].offRequestViolations[worker]))
                    if worker_line > total_lines:
                        total_lines = worker_line
        line += 1 + total_lines

    dias_de_la_semana = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]

    dias_violados = dict()
    if sum([weeklySolution[week].requirementViolations[day] for week in range(0,prm.NumberOfWeeks) for day in weeklySolution[week].requirementViolations.keys()]) > 0:
        for week in range(0,prm.NumberOfWeeks):
            for day in weeklySolution[week].requirementViolations.keys():
                if weeklySolution[week].requirementViolations[day] > 0:
                    dias_violados.setdefault(day,[]).append((week,weeklySolution[week].requirementViolations[day]))
        #Write Results
        worksheet1.write(line , 6, "Violaciones de trabajadores asignados")
        for day in sorted(dias_violados.keys()):
            worksheet1.write(line , 7, dias_de_la_semana[day])
            for value in dias_violados[day]:
                worksheet1.write(line , 8+value[0], value[1])
            line += 1
        line += 2


    if sum([weeklySolution[week].externalViolations for week in range(0,prm.NumberOfWeeks) ]) > 0:
        worksheet1.write(line , 6, "Violaciones Externas")
        for week in range(0,prm.NumberOfWeeks):
            if weeklySolution[week].externalViolations > 0:
                worksheet1.write(line , 8+week, weeklySolution[week].externalViolations)
        line += 2

    line += 1
    worksheet1.write(line , 6, "Domingos trabajados")
    worksheet1.write(line , 8, "Total")
    line += 1
    for staffId in prm.GlobaldomingosPorMes.keys():
        worksheet1.write(line , 7, staffId)
        worksheet1.write(line , 8, prm.GlobaldomingosPorMes[staffId])
        line += 1
    worksheet1.set_column(6, 6, 40)  # set column width

    for week in range(0,prm.NumberOfWeeks+1):
        worksheet1.set_column(7+week, 7+week, 15)  # set column width
        # worksheet1.set_column(8, 8, 15)  # set column width
        # worksheet1.set_column(9, 9, 15)  # set column width
        # worksheet1.set_column(10, 10, 15)  # set column width
        # worksheet1.set_column(11, 11, 15)  # set column width

    worksheet1.write(line , 6, "Horas trabajadas")
    worksheet1.write(line , 8, "Total Contrato")
    worksheet1.write(line , 9, "Total Extras")
    worksheet1.write(line , 10, "Total")
    line += 1
    for staffId in prm.GlobaldomingosPorMes.keys():
        worksheet1.write(line , 7, staffId)
        worksheet1.write(line , 8, sum([weeklySolution[week].HorasContratoSemanales[staffId] for week in range(0,prm.NumberOfWeeks)])/60)
        worksheet1.write(line , 9, sum([weeklySolution[week].HorasExtraSemanales[staffId] for week in range(0,prm.NumberOfWeeks)])/60)
        worksheet1.write(line , 10, (sum([weeklySolution[week].HorasContratoSemanales[staffId] for week in range(0,prm.NumberOfWeeks)])+sum([weeklySolution[week].HorasExtraSemanales[staffId] for week in range(0,prm.NumberOfWeeks)]))/60)
        line += 1
    worksheet1.set_column(6, 6, 40)  # set column width

    for week in range(0,prm.NumberOfWeeks+1):
        worksheet1.set_column(7+week, 7+week, 15)  # set column width
        # worksheet1.set_column(8, 8, 15)  # set column width
        # worksheet1.set_column(9, 9, 15)  # set column width
        # worksheet1.set_column(10, 10, 15)  # set column width
        # worksheet1.set_column(11, 11, 15)  # set column width


    nro_a_mes = {1:'Enero',2:'Febrero',3:'Marzo',4:'Abril',5:'Mayo',6:'Junio',7:'Julio',
            8:'Agosto',9:'Septiembre',10:'Octubre',11:'Noviembre',12:'Diciembre'}

    fecha = prm.dia_inicio
    month_added = dict()
    for i in nro_a_mes.keys():
        month_added[i] = False

    for week in range(0,prm.NumberOfWeeks):
        if not month_added[fecha.month]:
            tmp_worksheet = workbook.add_worksheet(nro_a_mes[fecha.month])
            month_added[fecha.month] = True
        fecha += datetime.timedelta(weeks=1)

    workbook.close()
    writer.save()
    writer.close()
