import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


#### FOTOS for DEMO! user number
# Leer los datos del archivo Excel
df = pd.read_excel("src/Servicio/app/Demo/Libro1.xlsx", sheet_name="Hoja2",  index_col=0)

# # Ajustar el tamaño de la figura
# plt.figure(figsize=(8, 6))

# # Trazar las tres series con diferentes estilos de línea y marcadores
# df['100 Usuarios'].plot(label='100 Usuarios', color='blue')
# # df['75 Usuarios'].plot(label='75 Usuarios', color='green')
# # df['50 Usuarios'].plot(label='50 Usuarios', color='red')
# df['25 Usuarios'].plot(label='25 Usuarios', color='purple')
# plt.xticks(df.index[::5], rotation=90)
# # Título y etiquetas de los ejes
# plt.title('Number of Realized Recommendations')
# plt.xlabel('Time')
# plt.ylabel('Number of Tasks')
# plt.tight_layout()
# # Agregar una leyenda
# plt.legend()
# plt.grid(True, zorder=0)  # Establecer zorder para que el grid esté encima de la gráfica
# # Guardar la gráfica como una imagen
# plt.savefig('Number_of_Realized_Recommendations.jpg')
# plt.grid(True)

# # Mostrar la gráfica
# plt.show()



# # Leer los datos del archivo Excel


# # Crear una figura y cuatro subgráficas
# fig, axs = plt.subplots(2, 2, figsize=(12, 8), sharex=True)

# # Trazar la primera fila en la primera subgráfica (arriba a la izquierda)
# df['100 Usuarios'].plot(ax=axs[0, 0], color='blue', label='100 Users')
# df['100 Usuarios'].rolling(window=20).mean().plot(ax=axs[0, 0], color='black', label='Moving average (20)')
# axs[0, 0].legend()
# axs[0, 0].grid(True, zorder=0)  #)

# # Trazar la segunda fila en la segunda subgráfica (arriba a la derecha)
# df['75 Usuarios'].plot(ax=axs[0, 1], color='green', label='75 Users')
# df['75 Usuarios'].rolling(window=20).mean().plot(ax=axs[0, 1], color='black', label='Moving average (20)')
# axs[0, 1].legend()
# axs[0, 1].grid(True, zorder=0)  #)

# # Trazar la tercera fila en la tercera subgráfica (abajo a la izquierda)
# df['50 Usuarios'].plot(ax=axs[1, 0], color='red', label='50 User')
# df['50 Usuarios'].rolling(window=20).mean().plot(ax=axs[1, 0], color='black', label='Moving average (20)')
# axs[1, 0].legend()
# axs[1, 0].grid(True, zorder=0)  #)


# # Trazar la cuarta fila en la cuarta subgráfica (abajo a la derecha)
# df['25 Usuarios'].plot(ax=axs[1, 1], color='purple',label='25 Users')
# # axs[1, 1].set_title('25 Users')
# df['25 Usuarios'].rolling(window=20).mean().plot(ax=axs[1, 1], color='black', label='Moving average (20)')
# axs[1, 1].legend()
# axs[1, 1].grid(True, zorder=0)  #)


# # Ajustar la etiqueta del eje x en todas las subgráficas
# for ax in axs.flt:
#     ax.set_xlabel('Time')
#     ax.set_xticks(df.index[::5])
#     ax.tick_params(axis='x', rotation=90)
#     ax.set_ylabel('Number of Tasks')

# # Agregar un título global a la figura
# fig.suptitle('Number of Realized Recommendations', fontsize=16)

# # Ajustar el espaciado entre subgráficas
# plt.tight_layout()
# plt.savefig('2x2Number_of_Realized_Recommendations.jpg')
# # Mostrar la figura
# plt.show()




# # Crear una figura y cuatro subgráficas
# fig, (ax1, ax2, ax3,ax4) = plt.subplots(4, 1, figsize=(10, 10), sharex=True)
# # Trazar la primera fila en la primera subgráfica (arriba a la izquierda)
# df['100 Usuarios'].plot(ax=ax1, color='blue', label='100 Users')
# df['100 Usuarios'].rolling(window=20).mean().plot(ax=ax1, color='black', label='Moving average (20)')
# ax1.legend()
# ax1.grid(True, zorder=0)  #)

# # Trazar la segunda fila en la segunda subgráfica (arriba a la derecha)
# df['75 Usuarios'].plot(ax=ax2, color='green', label='75 Users')
# df['75 Usuarios'].rolling(window=20).mean().plot(ax=ax2, color='black', label='Moving average (20)')
# ax2.legend()
# ax2.grid(True, zorder=0)  #)

# # Trazar la tercera fila en la tercera subgráfica (abajo a la izquierda)
# df['50 Usuarios'].plot(ax=ax3, color='red', label='50 User')
# df['50 Usuarios'].rolling(window=20).mean().plot(ax=ax3, color='black', label='Moving average (20)')
# ax3.legend()
# ax3.grid(True, zorder=0)  #)


# # Trazar la cuarta fila en la cuarta subgráfica (abajo a la derecha)
# df['25 Usuarios'].plot(ax=ax4, color='purple',label='25 Users')
# # axs[1, 1].set_title('25 Users')
# df['25 Usuarios'].rolling(window=20).mean().plot(ax=ax4, color='black', label='Moving average (20)')
# ax4.legend()
# ax4.grid(True, zorder=0)  #)


# # Ajustar la etiqueta del eje x en todas las subgráficas
# for ax in [ax1,ax2,ax3,ax4]:
#     ax.set_xlabel('Time')
#     ax.set_xticks(df.index[::5])
#     ax.tick_params(axis='x', rotation=90)
#     ax.set_ylabel('Number of Tasks')

# # Agregar un título global a la figura
# fig.suptitle('Number of Realized Recommendations', fontsize=16)

# # Ajustar el espaciado entre subgráficas
# plt.tight_layout()
# plt.savefig('Fila_Number_of_Realized_Recommendations.jpg')
# # Mostrar la figura
# plt.show()
# import pandas as pd
# import matplotlib.pyplot as plt

# # Leer los datos del archivo Excel
# df = pd.read_excel("src/Servicio/app/Demo/Piloto_deusto.xlsx", sheet_name="Hoja1",  index_col=0)

# # Convertir el índice a cadena de texto
# df.index = df.index.astype(str)
# index_new=[]
# for i in df.index:
#     index_new.append(i[:-3])  
# df.index=index_new
# # Ajustar el tamaño de la figura
# plt.figure(figsize=(8, 3))
# # df.plot()
# # Trazar las columnas deseadas
# for column in df.columns:
#     plt.plot(df.index, df[column])

# plt.xticks(df.index[::5], rotation=90)

# # Título y etiquetas de los ejes
# plt.title('Number of Realized Recommendations')
# plt.xlabel('Time')
# plt.ylabel('Number of Tasks')

# plt.tight_layout()
# plt.grid(True, zorder=0)  # Establecer zorder para que el grid esté encima de la gráfica

# # Guardar la gráfica como una imagen
# plt.savefig('Deusto_pilot_Number_of_Realized_Recommendations.jpg')

# # Mostrar la gráfica
# plt.show()



############# ---- user abailable 
import pandas as pd
import matplotlib.pyplot as plt

# Cargar los datos
df = pd.read_excel("src/Servicio/app/Demo/Libro1.xlsx", sheet_name="Hoja4", index_col=0)
# df.index = pd.to_datetime(df.index)  # Convertir el índice a formato de fecha y hora

# Crear una figura y dos subgráficas arriba y una abajo
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

# Trazar cada serie en las subgráficas correspondientes
df['0.75 user avalable'].plot(ax=ax1, color='blue', label='User available  = 0,25')
df['0.75 user avalable'].rolling(window=20).mean().plot(ax=ax1, color='black', label='Moving average (20)')
ax1.legend()
ax1.grid(True, zorder=0)

df['0.5 user avalable'].plot(ax=ax2, color='green', label='User available  = 0,5')
df['0.5 user avalable'].rolling(window=20).mean().plot(ax=ax2, color='black', label='Moving average (20)')
ax2.legend()
ax2.grid(True, zorder=0)

df['0.25 user avalable'].plot(ax=ax3, color='red', label='User available  = 0,75')
df['0.25 user avalable'].rolling(window=20).mean().plot(ax=ax3, color='black', label='Moving average (20)')
ax3.legend()
ax3.grid(True, zorder=0)

# Ajustar las etiquetas del eje x en todas las subgráficas
for ax in [ax1, ax2, ax3]:
    ax.set_xlabel('Time')
    ax.set_ylabel('Number of Tasks')
    ax.set_xticks(df.index[::5])
    # ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M:%S'))
    ax.tick_params(axis='x', rotation=90)
    ax.set_ylim(bottom=0)
    # if ax==ax1:
    #     ax.set_ylim(top=4)
    # if ax==ax2:
    #     ax.set_ylim(top=7)
    # if ax==ax3:
    #     ax.set_ylim(top=5)

    # Configurar los límites del eje y para mostrar solo etiquetas enteras
    # y_ticks = ax.get_yticks()
    # ax.set_yticks(y_ticks[y_ticks.astype(int) == y_ticks])
# Agregar un título global a la figura
fig.suptitle('Number of Realized Recommendations', fontsize=16)

# Ajustar el espaciado entre subgráficas
plt.tight_layout()

# Guardar la figura como imagen
plt.savefig('3x1User_abalable_Number_of_Realized_Recommendations.jpg')

# Mostrar la figura
plt.show()




############# ---- user abailable 
import pandas as pd
import matplotlib.pyplot as plt

# Cargar los datos
df = pd.read_excel("src/Servicio/app/Demo/Libro1.xlsx", sheet_name="Hoja5", index_col=0)
# df.index = pd.to_datetime(df.index)  # Convertir el índice a formato de fecha y hora

# Crear una figura y dos subgráficas arriba y una abajo
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

# Trazar cada serie en las subgráficas correspondientes
df['0.75 uer realized'].plot(ax=ax1, color='blue', label='User realized variable = 0,25')
df['0.75 uer realized'].rolling(window=20).mean().plot(ax=ax1, color='black', label='Moving average (20)')
ax1.legend()
ax1.grid(True, zorder=0)

df['0.5  uer realized'].plot(ax=ax2, color='green', label='User realized variable = 0,5')
df['0.5  uer realized'].rolling(window=20).mean().plot(ax=ax2, color='black', label='Moving average (20)')
ax2.legend()
ax2.grid(True, zorder=0)

df['0.25  uer realized'].plot(ax=ax3, color='red', label='User realized variable = 0,75')
df['0.25  uer realized'].rolling(window=20).mean().plot(ax=ax3, color='black', label='Moving average (20)')
ax3.legend()
ax3.grid(True, zorder=0)

# Ajustar las etiquetas del eje x en todas las subgráficas
for ax in [ax1, ax2, ax3]:
    ax.set_xlabel('Time')
    ax.set_ylabel('Number of Tasks')
    ax.set_xticks(df.index[::5])
    # ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M:%S'))
    ax.tick_params(axis='x', rotation=90)
    ax.set_ylim(bottom=0)
    # if ax==ax1:
    #     ax.set_ylim(top=4)
    # if ax==ax2:
    #     ax.set_ylim(top=7)
    # if ax==ax3:
    #     ax.set_ylim(top=5)

    # Configurar los límites del eje y para mostrar solo etiquetas enteras
    # y_ticks = ax.get_yticks()
    # ax.set_yticks(y_ticks[y_ticks.astype(int) == y_ticks])
# Agregar un título global a la figura
fig.suptitle('Number of Realized Recommendations', fontsize=16)

# Ajustar el espaciado entre subgráficas
plt.tight_layout()

# Guardar la figura como imagen
plt.savefig('3x1User_realized_Number_of_Realized_Recommendations.jpg')

# Mostrar la figura
plt.show()