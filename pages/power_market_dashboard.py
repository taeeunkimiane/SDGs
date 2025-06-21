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

# CSV 파일 경로 설정
CSV_FILE_PATH = '2023년도 전력시장통계.csv'

@st.cache_data
def load_data():
    """데이터 로드 및 전처리"""
    try:
        # 파일을 라인별로 읽어서 처리
        with open(CSV_FILE_PATH, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # 데이터 시작점과 헤더 찾기
        data_lines = []
        header_line = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # CSV 파싱
            parts = [part.strip(' "') for part in line.split(',')]
            
            # 영어 헤더 라인 찾기 (Gyeonggi가 포함된 라인)
            if 'Gyeonggi' in line and header_line is None:
                header_line = parts
                continue
            
            # 데이터 라인 찾기 (연도로 시작하는 라인)
            if len(parts) > 0 and parts[0].isdigit() and len(parts[0]) == 4:
                data_lines.append(parts)
        
        if not data_lines:
            raise ValueError("데이터를 찾을 수 없습니다.")
        
        # 헤더 설정
        if header_line:
            # 빈 헤더 처리
            headers = []
            for i, header in enumerate(header_line):
                if header.strip() == '' or header == 'nan':
                    if i == 0:
                        headers.append('Year')
                    else:
                        headers.append(f'Column_{i}')
                else:
                    if i == 0:
                        headers.append('Year')
                    else:
                        headers.append(header)
        else:
            # 기본 헤더 생성
            max_cols = max(len(line) for line in data_lines)
            headers = ['Year'] + [f'Column_{i}' for i in range(1, max_cols)]
        
        # DataFrame 생성
        df = pd.DataFrame(data_lines, columns=headers[:len(data_lines[0])])
        
        # 데이터 타입 변환
        # Year 컬럼을 정수로 변환
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        
        # 숫자형 컬럼들 처리
        for col in df.columns[1:]:  # Year 컬럼 제외
            if col in df.columns:
                # 문자열 정리 및 숫자 변환
                df[col] = df[col].astype(str)
                df[col] = df[col].str.replace(',', '')  # 쉼표 제거
                df[col] = df[col].str.replace(' ', '')   # 공백 제거
                df[col] = df[col].str.replace('\"', '')  # 따옴표 제거
                
                # 숫자로 변환 시도
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # NaN이 너무 많은 컬럼 제거 (80% 이상이 NaN인 컬럼)
        threshold = len(df) * 0.2  # 20% 이상 데이터가 있는 컬럼만 유지
        df = df.dropna(axis=1, thresh=threshold)
        
        # 빈 행 제거
        df = df.dropna(subset=['Year'])
        df = df.reset_index(drop=True)
        
        # 컬럼명 정리 (알려진 지역명으로 매핑)
        region_mapping = {
            'Gyeonggi': '경기',
            'Gangwon': '강원', 
            'Gyeongnam': '경남',
            'Gyeongbuk': '경북',
            'Jeonnam': '전남',
            'Jeonbuk': '전북',
            'Chungnam': '충남',
            'Chungbuk': '충북',
            'Jeju': '제주',
            'Seoul': '서울',
            'Incheon': '인천',
            'Daejeon': '대전',
            'Gwangju': '광주',
            'Daegu': '대구',
            'Sejong': '세종',
            'Ulsan': '울산',
            'Busan': '부산'
        }
        
        # 컬럼명 변경
        new_columns = {}
        for col in df.columns:
            if col in region_mapping:
                new_columns[col] = region_mapping[col]
        
        if new_columns:
            df = df.rename(columns=new_columns)
        
        st.success(f"✅ 데이터 로드 성공! (총 {len(df)}행, {len(df.columns)}열)")
        return df
        
    except FileNotFoundError:
        st.error(f"❌ CSV 파일을 찾을 수 없습니다: {CSV_FILE_PATH}")
        st.info("현재 디렉토리에 '2023년도 전력시장통계.csv' 파일이 있는지 확인해주세요.")
        st.stop()
    except Exception as e:
        st.error(f"❌ 데이터 로드 중 오류 발생: {str(e)}")
        st.stop()

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
        if 'Year' in df.columns:
            year_range = f"{int(df['Year'].min())}-{int(df['Year'].max())}"
        else:
            year_range = "N/A"
        st.metric(
            label="연도 범위",
            value=year_range,
            delta=None
        )

def create_data_overview(df):
    """데이터 개요 섹션"""
    st.subheader("📊 데이터 개요")
    
    # 요약 지표
    create_summary_metrics(df)
    
    # 데이터 품질 정보
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**컬럼 정보:**")
        st.write(f"- 총 컬럼 수: {len(df.columns)}개")
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        st.write(f"- 수치형 컬럼: {len(numeric_cols)}개")
        
        # 주요 컬럼 표시
        st.write("**주요 컬럼들:**")
        display_cols = [col for col in df.columns if col != 'Year'][:10]
        for col in display_cols:
            non_null_count = df[col].count()
            st.write(f"- {col}: {non_null_count}개 데이터")
    
    with col2:
        st.write("**데이터 샘플:**")
        st.dataframe(df.head(5), use_container_width=True)

def create_data_filter(df):
    """데이터 필터링 기능"""
    st.subheader("🔍 데이터 필터링")
    
    # 연도 필터링
    if 'Year' in df.columns:
        year_min, year_max = int(df['Year'].min()), int(df['Year'].max())
        selected_years = st.slider(
            "연도 범위 선택:",
            min_value=year_min,
            max_value=year_max,
            value=(year_min, year_max)
        )
        filtered_df = df[(df['Year'] >= selected_years[0]) & (df['Year'] <= selected_years[1])].copy()
    else:
        filtered_df = df.copy()
    
    # 컬럼 선택
    available_cols = [col for col in df.columns if df[col].count() > 0]  # 데이터가 있는 컬럼만
    default_cols = ['Year'] if 'Year' in available_cols else []
    
    # 수치형 컬럼 중 데이터가 많은 순으로 선택
    numeric_cols = []
    for col in available_cols:
        if col != 'Year' and pd.api.types.is_numeric_dtype(df[col]):
            numeric_cols.append((col, df[col].count()))
    
    # 데이터 개수로 정렬하여 상위 컬럼들 추가
    numeric_cols.sort(key=lambda x: x[1], reverse=True)
    default_cols.extend([col[0] for col in numeric_cols[:8]])
    
    selected_columns = st.multiselect(
        "표시할 컬럼을 선택하세요:",
        options=available_cols,
        default=default_cols
    )
    
    if not selected_columns:
        st.warning("최소 하나의 컬럼을 선택해주세요.")
        return df.head(50)
    
    filtered_df = filtered_df[selected_columns].copy()
    
    # 행 수 제한
    max_rows = st.slider("표시할 최대 행 수", 10, min(500, len(filtered_df)), 50)
    
    return filtered_df.head(max_rows)

def create_visualizations(df):
    """다양한 시각화 생성"""
    st.subheader("📈 데이터 시각화")
    
    # 데이터가 있는 수치형 컬럼만 선택
    numeric_cols = []
    for col in df.columns:
        if col != 'Year' and pd.api.types.is_numeric_dtype(df[col]) and df[col].count() > 0:
            numeric_cols.append(col)
    
    if len(numeric_cols) == 0:
        st.warning("시각화할 수치형 데이터가 없습니다.")
        return
    
    # 시각화 타입 선택
    viz_type = st.selectbox(
        "시각화 유형을 선택하세요:",
        ["시계열 그래프", "막대 그래프", "히스토그램", "박스 플롯", "상관관계 히트맵", "지역별 비교"]
    )
    
    if viz_type == "시계열 그래프":
        # 데이터가 많은 컬럼들을 기본으로 선택
        data_counts = [(col, df[col].count()) for col in numeric_cols]
        data_counts.sort(key=lambda x: x[1], reverse=True)
        default_selection = [col[0] for col in data_counts[:5]]
        
        selected_cols = st.multiselect(
            "시각화할 컬럼들 선택:", 
            numeric_cols, 
            default=default_selection
        )
        
        if selected_cols and 'Year' in df.columns:
            fig = go.Figure()
            
            for col in selected_cols:
                # NaN이 아닌 데이터만 필터링
                valid_data = df[df[col].notna()]
                if len(valid_data) > 0:
                    fig.add_trace(go.Scatter(
                        x=valid_data['Year'], 
                        y=valid_data[col], 
                        mode='lines+markers',
                        name=col,
                        line=dict(width=2),
                        connectgaps=False
                    ))
            
            fig.update_layout(
                title="연도별 추이",
                xaxis_title="연도",
                yaxis_title="값",
                hovermode='x unified',
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
    
    elif viz_type == "막대 그래프":
        col_to_plot = st.selectbox("시각화할 컬럼 선택:", numeric_cols)
        if col_to_plot and 'Year' in df.columns:
            # 데이터가 있는 행만 필터링
            valid_data = df[df[col_to_plot].notna()].copy()
            if len(valid_data) > 0:
                # 최근 10년 또는 모든 데이터
                recent_data = valid_data.tail(min(10, len(valid_data)))
                fig = px.bar(recent_data, x='Year', y=col_to_plot, 
                            title=f"{col_to_plot} - 연도별 현황")
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"{col_to_plot} 컬럼에 유효한 데이터가 없습니다.")
    
    elif viz_type == "히스토그램":
        col_to_plot = st.selectbox("시각화할 컬럼 선택:", numeric_cols)
        if col_to_plot:
            valid_data = df[df[col_to_plot].notna()][col_to_plot]
            if len(valid_data) > 0:
                bins = st.slider("구간 수", 5, 30, 15)
                fig = px.histogram(x=valid_data, nbins=bins, 
                                 title=f"{col_to_plot} 분포")
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"{col_to_plot} 컬럼에 유효한 데이터가 없습니다.")
    
    elif viz_type == "박스 플롯":
        # 데이터가 많은 상위 컬럼들 선택
        data_counts = [(col, df[col].count()) for col in numeric_cols]
        data_counts.sort(key=lambda x: x[1], reverse=True)
        default_selection = [col[0] for col in data_counts[:5]]
        
        cols_to_plot = st.multiselect("시각화할 컬럼들 선택:", numeric_cols, 
                                    default=default_selection)
        if cols_to_plot:
            fig = go.Figure()
            for col in cols_to_plot:
                valid_data = df[df[col].notna()][col]
                if len(valid_data) > 0:
                    fig.add_trace(go.Box(y=valid_data, name=col))
            
            fig.update_layout(title="박스 플롯 비교", height=500)
            st.plotly_chart(fig, use_container_width=True)
    
    elif viz_type == "상관관계 히트맵":
        if len(numeric_cols) > 1:
            # 데이터가 많은 컬럼들만 선택
            data_counts = [(col, df[col].count()) for col in numeric_cols]
            data_counts.sort(key=lambda x: x[1], reverse=True)
            available_cols = [col[0] for col in data_counts if col[1] > 5]  # 최소 5개 데이터
            
            if len(available_cols) > 1:
                default_selection = available_cols[:6]
                corr_cols = st.multiselect("상관관계를 볼 컬럼들 선택:", available_cols, 
                                         default=default_selection)
                if len(corr_cols) > 1:
                    # 유효한 데이터만으로 상관관계 계산
                    corr_data = df[corr_cols].dropna()
                    if len(corr_data) > 1:
                        corr_matrix = corr_data.corr()
                        fig = px.imshow(corr_matrix, text_auto=True, aspect="auto", 
                                       title="상관관계 히트맵", 
                                       color_continuous_scale='RdBu_r')
                        fig.update_layout(height=500)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("상관관계 분석을 위한 충분한 데이터가 없습니다.")
            else:
                st.warning("상관관계 분석을 위한 유효한 컬럼이 부족합니다.")
        else:
            st.info("상관관계 분석을 위해서는 최소 2개의 수치형 컬럼이 필요합니다.")
    
    elif viz_type == "지역별 비교":
        # 한국 지역명이 포함된 컬럼들 찾기
        korean_regions = ['경기', '서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', 
                         '경남', '경북', '전남', '전북', '충남', '충북', '강원', '제주']
        
        region_cols = []
        for col in df.columns:
            if any(region in str(col) for region in korean_regions) and pd.api.types.is_numeric_dtype(df[col]):
                if df[col].count() > 0:  # 데이터가 있는 컬럼만
                    region_cols.append(col)
        
        if region_cols:
            # 데이터가 많은 지역들을 기본 선택
            data_counts = [(col, df[col].count()) for col in region_cols]
            data_counts.sort(key=lambda x: x[1], reverse=True)
            default_selection = [col[0] for col in data_counts[:8]]
            
            selected_regions = st.multiselect("비교할 지역들 선택:", region_cols, 
                                            default=default_selection)
            
            if selected_regions and 'Year' in df.columns:
                fig = go.Figure()
                
                for region in selected_regions:
                    valid_data = df[df[region].notna()]
                    if len(valid_data) > 0:
                        fig.add_trace(go.Scatter(
                            x=valid_data['Year'], 
                            y=valid_data[region], 
                            mode='lines+markers',
                            name=region,
                            line=dict(width=2),
                            connectgaps=False
                        ))
                
                fig.update_layout(
                    title="지역별 비교",
                    xaxis_title="연도",
                    yaxis_title="값",
                    hovermode='x unified',
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("지역별 데이터를 찾을 수 없습니다.")

def create_statistics_section(df):
    """통계 분석 섹션"""
    st.subheader("📊 통계 분석")
    
    # 기본 통계 요약
    if st.checkbox("기본 통계 요약 보기"):
        st.write("**기술통계량:**")
        # 수치형 컬럼만 선택하고 데이터가 있는 것만
        numeric_data = df.select_dtypes(include=[np.number])
        valid_cols = [col for col in numeric_data.columns if numeric_data[col].count() > 0]
        if valid_cols:
            st.dataframe(numeric_data[valid_cols].describe())
        else:
            st.warning("표시할 통계 데이터가 없습니다.")
    
    # 개별 컬럼 분석
    numeric_cols = [col for col in df.columns 
                   if col != 'Year' and pd.api.types.is_numeric_dtype(df[col]) and df[col].count() > 0]
    
    if numeric_cols:
        st.write("**개별 컬럼 분석:**")
        selected_col = st.selectbox("분석할 컬럼 선택:", numeric_cols)
        
        if selected_col:
            valid_data = df[df[selected_col].notna()][selected_col]
            
            if len(valid_data) > 0:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("평균", f"{valid_data.mean():,.2f}")
                    st.metric("중앙값", f"{valid_data.median():,.2f}")
                
                with col2:
                    st.metric("표준편차", f"{valid_data.std():,.2f}")
                    st.metric("최솟값", f"{valid_data.min():,.2f}")
                
                with col3:
                    st.metric("최댓값", f"{valid_data.max():,.2f}")
                    st.metric("데이터 개수", f"{len(valid_data):,}")
                
                # 연평균 증가율 계산 (Year 컬럼이 있는 경우)
                if 'Year' in df.columns and len(valid_data) > 1:
                    yearly_data = df[df[selected_col].notna()][['Year', selected_col]].sort_values('Year')
                    if len(yearly_data) > 1:
                        first_val = yearly_data[selected_col].iloc[0]
                        last_val = yearly_data[selected_col].iloc[-1]
                        years = yearly_data['Year'].iloc[-1] - yearly_data['Year'].iloc[0]
                        
                        if first_val > 0 and years > 0:
                            growth_rate = ((last_val / first_val) ** (1/years) - 1) * 100
                            st.metric("연평균 증가율", f"{growth_rate:.2f}%")

def run():
    # 헤더
    st.markdown('<h1 class="main-header">⚡ 전력시장통계 대시보드</h1>', unsafe_allow_html=True)
    
    # 데이터 로드
    with st.spinner('데이터를 로드하는 중...'):
        df = load_data()
    
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
        st.dataframe(filtered_df, use_container_width=True, height=400)
        
    elif selected_menu == "시각화":
        create_visualizations(df)
        
    elif selected_menu == "통계 분석":
        create_statistics_section(df)
        
    elif selected_menu == "데이터 다운로드":
        st.subheader("💾 데이터 다운로드")
        
        # 필터링된 데이터 다운로드
        filtered_df = create_data_filter(df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV 다운로드
            csv_data = filtered_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📄 CSV 파일로 다운로드",
                data=csv_data,
                file_name=f"power_market_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Excel 다운로드
            try:
                import io
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    filtered_df.to_excel(writer, index=False, sheet_name='전력시장통계')
                excel_data = output.getvalue()
                
                st.download_button(
                    label="📊 Excel 파일로 다운로드",
                    data=excel_data,
                    file_name=f"power_market_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except ImportError:
                st.info("💡 Excel 다운로드를 위해 openpyxl 패키지 설치가 필요합니다.")
        
        # 데이터 미리보기
        st.write("**다운로드될 데이터 미리보기:**")
        st.dataframe(filtered_df.head(10), use_container_width=True)
        st.info(f"총 {len(filtered_df)}행의 데이터가 다운로드됩니다.")
    
    # 푸터
    st.sidebar.markdown("---")
    st.sidebar.info("💡 이 대시보드는 전력시장 통계 데이터를 분석하기 위해 제작되었습니다.")
    
    # 데이터 소스 정보
    with st.sidebar.expander("📋 데이터 정보"):
        st.write("**데이터 소스:** 전력시장통계 CSV 파일")
        st.write(f"**로드된 데이터:** {len(df)}행 × {len(df.columns)}열")
        if 'Year' in df.columns:
            st.write(f"**연도 범위:** {int(df['Year'].min())} - {int(df['Year'].max())}")
        
        # 유효한 데이터가 있는 컬럼 수 표시
        valid_cols = [col for col in df.columns if df[col].count() > 0]
        st.write(f"**유효한 컬럼:** {len(valid_cols)}개")
        
        # 주요 지역 정보
        korean_regions = ['경기', '서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', 
                         '경남', '경북', '전남', '전북', '충남', '충북', '강원', '제주']
        region_cols = [col for col in df.columns if any(region in str(col) for region in korean_regions)]
        if region_cols:
            st.write(f"**포함된 지역:** {len(region_cols)}개")

if __name__ == "__main__":
    run()
