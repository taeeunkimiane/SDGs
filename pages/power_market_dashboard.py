import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title="전력시장 통계 대시보드",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem;
    }
    .stSelectbox > div > div {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# CSV 파일 경로
csv_file = '/mnt/data/2023년도 전력시장통계.csv'

@st.cache_data
def load_data():
    """데이터 로드 및 전처리"""
    try:
        df = pd.read_csv(csv_file, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(csv_file, encoding='cp949')
    
    # 날짜 컬럼이 있다면 변환
    for col in df.columns:
        if '날짜' in col or '일시' in col or 'date' in col.lower():
            try:
                df[col] = pd.to_datetime(df[col])
            except:
                pass
    
    return df

def create_summary_metrics(df):
    """주요 지표 요약 생성"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="전체 데이터 수",
            value=f"{len(df):,}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="컬럼 수",
            value=f"{len(df.columns)}",
            delta=None
        )
    
    with col3:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        st.metric(
            label="수치형 컬럼",
            value=f"{len(numeric_cols)}",
            delta=None
        )
    
    with col4:
        missing_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        st.metric(
            label="결측치 비율",
            value=f"{missing_percentage:.1f}%",
            delta=None
        )

def create_data_overview(df):
    """데이터 개요 섹션"""
    st.subheader("📊 데이터 개요")
    
    # 요약 지표
    create_summary_metrics(df)
    
    # 데이터 타입 정보
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**데이터 타입별 컬럼 수:**")
        dtype_counts = df.dtypes.value_counts()
        for dtype, count in dtype_counts.items():
            st.write(f"- {dtype}: {count}개")
    
    with col2:
        st.write("**결측치가 있는 컬럼:**")
        missing_cols = df.isnull().sum()
        missing_cols = missing_cols[missing_cols > 0].sort_values(ascending=False)
        if len(missing_cols) > 0:
            for col, count in missing_cols.items():
                percentage = (count / len(df)) * 100
                st.write(f"- {col}: {count}개 ({percentage:.1f}%)")
        else:
            st.write("결측치가 없습니다! ✅")

def create_data_filter(df):
    """데이터 필터링 기능"""
    st.subheader("🔍 데이터 필터링")
    
    # 컬럼 선택
    selected_columns = st.multiselect(
        "표시할 컬럼을 선택하세요:",
        options=df.columns.tolist(),
        default=df.columns.tolist()[:10] if len(df.columns) > 10 else df.columns.tolist()
    )
    
    if not selected_columns:
        st.warning("최소 하나의 컬럼을 선택해주세요.")
        return df
    
    filtered_df = df[selected_columns].copy()
    
    # 수치형 데이터 필터링
    numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        st.write("**수치형 데이터 범위 설정:**")
        for col in numeric_cols[:3]:  # 처음 3개만 표시
            col_min, col_max = float(filtered_df[col].min()), float(filtered_df[col].max())
            if col_min != col_max:
                range_values = st.slider(
                    f"{col} 범위",
                    min_value=col_min,
                    max_value=col_max,
                    value=(col_min, col_max),
                    key=f"slider_{col}"
                )
                filtered_df = filtered_df[
                    (filtered_df[col] >= range_values[0]) & 
                    (filtered_df[col] <= range_values[1])
                ]
    
    # 행 수 제한
    max_rows = st.slider("표시할 최대 행 수", 10, min(1000, len(filtered_df)), 100)
    
    return filtered_df.head(max_rows)

def create_visualizations(df):
    """다양한 시각화 생성"""
    st.subheader("📈 데이터 시각화")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) == 0:
        st.warning("시각화할 수치형 데이터가 없습니다.")
        return
    
    # 시각화 타입 선택
    viz_type = st.selectbox(
        "시각화 유형을 선택하세요:",
        ["선 그래프", "막대 그래프", "히스토그램", "박스 플롯", "상관관계 히트맵", "산점도"]
    )
    
    if viz_type == "선 그래프":
        col_to_plot = st.selectbox("시각화할 컬럼 선택:", numeric_cols)
        if col_to_plot:
            fig = px.line(df, y=col_to_plot, title=f"{col_to_plot} 시계열 변화")
            st.plotly_chart(fig, use_container_width=True)
    
    elif viz_type == "막대 그래프":
        col_to_plot = st.selectbox("시각화할 컬럼 선택:", numeric_cols)
        if col_to_plot:
            # 상위 20개만 표시
            top_data = df.nlargest(20, col_to_plot)
            fig = px.bar(top_data, y=col_to_plot, title=f"{col_to_plot} 상위 20개")
            st.plotly_chart(fig, use_container_width=True)
    
    elif viz_type == "히스토그램":
        col_to_plot = st.selectbox("시각화할 컬럼 선택:", numeric_cols)
        if col_to_plot:
            bins = st.slider("구간 수", 10, 100, 30)
            fig = px.histogram(df, x=col_to_plot, nbins=bins, title=f"{col_to_plot} 분포")
            st.plotly_chart(fig, use_container_width=True)
    
    elif viz_type == "박스 플롯":
        cols_to_plot = st.multiselect("시각화할 컬럼들 선택:", numeric_cols, default=numeric_cols[:3])
        if cols_to_plot:
            fig = go.Figure()
            for col in cols_to_plot:
                fig.add_trace(go.Box(y=df[col], name=col))
            fig.update_layout(title="박스 플롯 비교")
            st.plotly_chart(fig, use_container_width=True)
    
    elif viz_type == "상관관계 히트맵":
        if len(numeric_cols) > 1:
            corr_cols = st.multiselect("상관관계를 볼 컬럼들 선택:", numeric_cols, default=numeric_cols[:5])
            if len(corr_cols) > 1:
                corr_matrix = df[corr_cols].corr()
                fig = px.imshow(corr_matrix, text_auto=True, aspect="auto", 
                               title="상관관계 히트맵")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("상관관계 분석을 위해서는 최소 2개의 수치형 컬럼이 필요합니다.")
    
    elif viz_type == "산점도":
        if len(numeric_cols) >= 2:
            col1, col2 = st.columns(2)
            with col1:
                x_col = st.selectbox("X축 컬럼:", numeric_cols, key="scatter_x")
            with col2:
                y_col = st.selectbox("Y축 컬럼:", numeric_cols, key="scatter_y", index=1)
            
            if x_col != y_col:
                fig = px.scatter(df, x=x_col, y=y_col, title=f"{x_col} vs {y_col}")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("산점도를 위해서는 최소 2개의 수치형 컬럼이 필요합니다.")

def create_statistics_section(df):
    """통계 분석 섹션"""
    st.subheader("📊 통계 분석")
    
    # 기본 통계 요약
    if st.checkbox("기본 통계 요약 보기"):
        st.write("**기술통계량:**")
        st.dataframe(df.describe(include='all'))
    
    # 고급 통계 분석
    st.write("**고급 통계 분석:**")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) > 0:
        selected_col = st.selectbox("분석할 컬럼 선택:", numeric_cols)
        
        if selected_col:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("평균", f"{df[selected_col].mean():.2f}")
                st.metric("중앙값", f"{df[selected_col].median():.2f}")
            
            with col2:
                st.metric("표준편차", f"{df[selected_col].std():.2f}")
                st.metric("분산", f"{df[selected_col].var():.2f}")
            
            with col3:
                st.metric("최솟값", f"{df[selected_col].min():.2f}")
                st.metric("최댓값", f"{df[selected_col].max():.2f}")

def run():
    # 헤더
    st.markdown('<h1 class="main-header">⚡ 2023년 전력시장통계 대시보드</h1>', unsafe_allow_html=True)
    
    # 데이터 로드
    try:
        df = load_data()
    except FileNotFoundError:
        st.error("CSV 파일을 찾을 수 없습니다. 파일 경로를 확인해주세요.")
        st.stop()
    except Exception as e:
        st.error(f"데이터 로드 중 오류가 발생했습니다: {str(e)}")
        st.stop()
    
    # 사이드바 메뉴
    st.sidebar.title("📋 메뉴")
    menu_options = ["데이터 개요", "데이터 보기", "시각화", "통계 분석", "데이터 다운로드"]
    selected_menu = st.sidebar.selectbox("메뉴를 선택하세요:", menu_options)
    
    # 메뉴별 화면 표시
    if selected_menu == "데이터 개요":
        create_data_overview(df)
        
    elif selected_menu == "데이터 보기":
        st.subheader("📋 데이터 테이블")
        filtered_df = create_data_filter(df)
        st.dataframe(filtered_df, use_container_width=True)
        
    elif selected_menu == "시각화":
        create_visualizations(df)
        
    elif selected_menu == "통계 분석":
        create_statistics_section(df)
        
    elif selected_menu == "데이터 다운로드":
        st.subheader("💾 데이터 다운로드")
        
        # 필터링된 데이터 다운로드
        filtered_df = create_data_filter(df)
        
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="CSV 파일로 다운로드",
            data=csv_data,
            file_name=f"filtered_power_market_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        # Excel 다운로드
        try:
            excel_data = filtered_df.to_excel(index=False, engine='openpyxl')
            st.download_button(
                label="Excel 파일로 다운로드",
                data=excel_data,
                file_name=f"filtered_power_market_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except:
            st.info("Excel 다운로드를 위해 openpyxl 패키지가 필요합니다.")
    
    # 푸터
    st.sidebar.markdown("---")
    st.sidebar.info("💡 이 대시보드는 2023년 전력시장 통계 데이터를 분석하기 위해 제작되었습니다.")

if __name__ == "__main__":
    run()
