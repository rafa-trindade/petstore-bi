import streamlit as st


def aplicar_estilo():
    st.markdown(
        """
        <style> 

            #MainMenu {visibility: hidden;}    
            footer {visibility: hidden;}
            header {visibility: hidden;} 

            [data-testid="baseButton-headerNoPadding"] {
                color: #2d4f72;
            }
            [data-testid="stSidebarCollapseButton"] {
                display: unset;
            }
            
            .st-emotion-cache-1jicfl2 {
                padding: 1rem 5rem 1rem;        

            /* Estilo para o container principal das notificações */
            [data-testid="stNotification"][role="alert"] {
                border-radius: 10px !important; /* Mantém a borda arredondada */
            }

            /* Estilo para o conteúdo específico das notificações */
            [data-testid="stNotificationContentInfo"] {
                background-color: #bac2d0 !important; /* Cor de fundo para st.info */
                color: #34527e !important; /* Cor do texto para st.info */
            }
            [data-testid="stNotificationContentSuccess"] {
                background-color: #b5cbd1 !important; /* Cor de fundo para st.success */
                color: #1d6e85 !important; /* Cor do texto para st.success */
            }
            [data-testid="stNotificationContentError"] {
                background-color: #dcb5bb !important; /* Cor de fundo para st.error */
                color: #a32639 !important; /* Cor do texto para st.error */
            }

            /* Estilo para garantir que o container principal também tenha o mesmo fundo */
            [data-testid="stNotification"][role="alert"]:has([data-testid="stNotificationContentInfo"]) {
                background-color: #bac2d0 !important; /* Cor de fundo para o container principal de st.info */
                color: #34527e !important; /* Cor do texto para o container principal de st.info */
            }
            [data-testid="stNotification"][role="alert"]:has([data-testid="stNotificationContentSuccess"]) {
                background-color: #b5cbd1 !important; /* Cor de fundo para o container principal de st.success */
                color: #1d6e85 !important; /* Cor do texto para o container principal de st.success */
            }
            [data-testid="stNotificafrom prophet import Prophet

        </style>
        """,
        unsafe_allow_html=True
    )



    st.sidebar.markdown("""

        <div align="center">
            <a href="https://github.com/rafa-trindade/petstore-pipeline" target="_blank">
                    <img style="border-radius: 7px;"
                    src="https://img.shields.io/badge/petstore--pipeline-2B5482?style=for-the-badge&logo=github&logoColor=fff&logoWidth=40&scale=1" />
            </a>             
        </div>


        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="
            position: fixed; 
            bottom: 0;
            left: 0;
            right: 0; 
            width: 100%; 
            background-color: #c6d0d2; 
            padding: 2.5px; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            color: #2B5482; 
            font-size: 14px;
            gap: 8px
        ">
            <span>Developed by </span>
            <a href="https://github.com/rafa-trindade" target="_blank">
                <img style="border-radius: 4px;" src="https://img.shields.io/badge/-Rafael%20Trindade-2B5482?style=flat-square&logo=github&logoColor=E4E3E3" alt="GitHub Badge">
            </a>
        </div>

        """,
        unsafe_allow_html=True
    )