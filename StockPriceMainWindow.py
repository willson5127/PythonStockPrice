import json
import os
import sys
import datetime
from QtStockPriceMainWindow import Ui_MainWindow  # 導入轉換後的 UI 類
from QtStockPriceEditDialog import Ui_Dialog
from PySide6.QtWidgets import QApplication, QMainWindow, QDialog
from PySide6.QtGui import QStandardItemModel, QStandardItem
from enum import Enum

# 要把.ui檔變成.py
# cd D:\_2.code\PythonStockPrice
# pyside6-uic QtStockPriceEditDialog.ui -o QtStockPriceEditDialog.py
# pyside6-uic QtStockPriceMainWindow.ui -o QtStockPriceMainWindow.py

class TradingType( Enum ):
    BUY = 0
    SELL = 1

class TradingData( Enum ):
    TRADING_DATE = 0
    TRADING_TYPE = 1 # 0:買進, 1:賣出
    TRADING_PRICE = 2
    TRADING_COUNT = 3
    TRADING_FEE_DISCOUNT = 4

class TradingCost( Enum ):
    TRADING_VALUE = 0
    TRADING_FEE = 1
    TRADING_TAX = 2
    TRADING_INSURANCE = 3
    TRADING_TOTAL_COST = 4

class Computer():
    def compute_cost( n_trading_type, f_trading_price, n_trading_count, f_trading_fee_discount, b_extra_insurance, b_daying_trading ):

        n_trading_value = int( f_trading_price * n_trading_count )
        n_trading_fee = int( n_trading_value * 0.001425 * f_trading_fee_discount )
        if n_trading_fee < 20:
            n_trading_fee = 20
        if n_trading_type == TradingType.SELL:
            if b_daying_trading:
                n_trading_tax = int( n_trading_value * 0.0015 )
            else:
                n_trading_tax = int( n_trading_value * 0.003 )
        else:
            n_trading_tax = 0

        dict_result = {}
        dict_result[ TradingCost.TRADING_VALUE ] = n_trading_value
        dict_result[ TradingCost.TRADING_FEE ] = n_trading_fee
        dict_result[ TradingCost.TRADING_TAX ] = n_trading_tax
        dict_result[ TradingCost.TRADING_INSURANCE ] = 0
        dict_result[ TradingCost.TRADING_TOTAL_COST ] = n_trading_value + n_trading_fee + n_trading_tax
        return dict_result


class TradingDataDialog( QDialog ):
    def __init__( self, b_discount, f_discount_value, b_extra_insurance, parent = None ):
        super().__init__( parent )

        self.ui = Ui_Dialog()
        self.ui.setupUi( self )

        obj_current_date = datetime.datetime.today()
        self.ui.qtDateEdit.setDate( obj_current_date.date() )
        self.ui.qtDateEdit.setCalendarPopup( True )
        self.ui.qtDiscountCheckBox.setChecked( b_discount )
        self.ui.qtDiscountRateDoubleSpinBox.setValue( f_discount_value )

        self.ui.qtDiscountCheckBox.stateChanged.connect( self.on_discount_check_box_state_changed )
        self.ui.qtBuyRadioButton.toggled.connect( self.compute_cost )
        self.ui.qtSellRadioButton.toggled.connect( self.compute_cost )
        self.ui.qtCommonTradeRadioButton.toggled.connect( self.on_trading_type_changed )
        self.ui.qtOddTradeRadioButton.toggled.connect( self.on_trading_type_changed )
        self.ui.qtPriceDoubleSpinBox.valueChanged.connect( self.compute_cost )
        self.ui.qtCommonTradeCountSpinBox.valueChanged.connect( self.compute_cost )
        self.ui.qtOddTradeCountSpinBox.valueChanged.connect( self.compute_cost )
        self.ui.qtOkButtonBox.accepted.connect( self.accept_data )
        self.ui.qtOkButtonBox.rejected.connect( self.cancel )


        self.dict_trading_data = {}

    def on_discount_check_box_state_changed( self, state ):
        if state == 2:
            self.ui.qtDiscountRateDoubleSpinBox.setEnabled( True )
        else:
            self.ui.qtDiscountRateDoubleSpinBox.setEnabled( False )

        self.compute_cost()

    def accept_data( self ):

        if float( self.ui.qtTotalCostLineEdit.text() ) != 0:
            self.dict_trading_data[ TradingData.TRADING_DATE ] = self.ui.qtDateEdit.date().toString( "yyyy-MM-dd" )
            self.dict_trading_data[ TradingData.TRADING_TYPE ] = self.get_trading_type()
            self.dict_trading_data[ TradingData.TRADING_PRICE ] = self.ui.qtPriceDoubleSpinBox.value()
            self.dict_trading_data[ TradingData.TRADING_COUNT ] = self.get_trading_count()
            self.dict_trading_data[ TradingData.TRADING_FEE_DISCOUNT ] = self.get_trading_fee_discount() 

            self.accept()
        else:
            self.reject()
    
    def cancel( self ):
        print("cancel")
        self.reject()

    def on_trading_type_changed( self ):
        if self.ui.qtCommonTradeRadioButton.isChecked():
            self.ui.qtCommonTradeCountSpinBox.setEnabled( True )
            self.ui.qtOddTradeCountSpinBox.setEnabled( False )
        else:
            self.ui.qtCommonTradeCountSpinBox.setEnabled( False )
            self.ui.qtOddTradeCountSpinBox.setEnabled( True )

        self.compute_cost()

    def get_trading_type( self ):
        if self.ui.qtBuyRadioButton.isChecked():
            return TradingType.BUY
        else:
            return TradingType.SELL

    def get_trading_count( self ):
        if self.ui.qtCommonTradeRadioButton.isChecked():
            return self.ui.qtCommonTradeCountSpinBox.value() * 1000
        else:
            return self.ui.qtOddTradeCountSpinBox.value()
        
    def get_trading_fee_discount( self ):
        if self.ui.qtDiscountCheckBox.isChecked():
            return self.ui.qtDiscountRateDoubleSpinBox.value() / 10
        else:
            return 1

    def compute_cost( self ):
        e_trading_type = self.get_trading_type()
        f_trading_price = self.ui.qtPriceDoubleSpinBox.value()
        n_trading_count = self.get_trading_count()
        f_trading_fee_discount = self.get_trading_fee_discount() 
        
        dict_result = Computer.compute_cost( e_trading_type, f_trading_price, n_trading_count, f_trading_fee_discount, True, False )

        self.ui.qtTradingValueLineEdit.setText( format( dict_result[ TradingCost.TRADING_VALUE ], ',' ) )
        self.ui.qtFeeLineEdit.setText( format( dict_result[ TradingCost.TRADING_FEE ] ), ',' )
        self.ui.qtTaxLineEdit.setText( format( dict_result[ TradingCost.TRADING_TAX ] ), ',' )
        self.ui.qtTotalCostLineEdit.setText( format( dict_result[ TradingCost.TRADING_TOTAL_COST ] ), ',' )


class MainWindow( QMainWindow ):
    def __init__(self):
        super( MainWindow, self ).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi( self )  # 設置 UI

        self.per_stock_trading_data_model = QStandardItemModel( 0, 5 ) 
        self.ui.qtTradingDataTableView.setModel( self.per_stock_trading_data_model )
        self.ui.qtTradingDataTableView.horizontalHeader().setSectionsMovable( True )


        self.ui.qtDiscountCheckBox.stateChanged.connect( self.on_discount_check_box_state_changed )
        self.ui.qtAddTradingDataPushButton.clicked.connect( self.on_add_new_data_push_button_clicked )
        self.ui.qtDeleteDataPushButton.clicked.connect( self.on_delete_data_push_button_clicked )
        self.ui.qtEditDataPushButton.clicked.connect( self.on_edit_data_push_button_clicked )


        self.list_trading_data = []

        self.func_load_existing_trading_data()

    def on_discount_check_box_state_changed( self, state ):
        if state == 2:
            self.ui.qtDiscountRateDoubleSpinBox.setEnabled( True )
        else:
            self.ui.qtDiscountRateDoubleSpinBox.setEnabled( False )

    def on_add_new_data_push_button_clicked( self ):
        dialog = TradingDataDialog( self.ui.qtDiscountCheckBox.isChecked(), self.ui.qtDiscountRateDoubleSpinBox.value(), self.ui.qtExtraInsuranceFeeCheckBox.isChecked(), self )

        if dialog.exec():
            dict_trading_data = dialog.dict_trading_data
            self.list_trading_data.append( dict_trading_data )

            sorted_list = sorted( self.list_trading_data, key=lambda x: ( datetime.datetime.strptime( x[ TradingData.TRADING_DATE ], "%Y-%m-%d"), x[ TradingData.TRADING_TYPE ] ) )
            self.refresh_table( sorted_list )

    def func_load_existing_trading_data( self ):
        # 取得目前工作目錄
        current_dir = os.path.dirname( __file__ )
        # 組合JSON檔案的路徑
        json_file_path = os.path.join( current_dir, 'TradingData.json' )

        with open( json_file_path,'r', encoding='utf-8' ) as f:
            data = json.load( f )

        for item in data:
            dict_per_trading_data = {}
            if( item[ "stock_number" ] ):
                str_stock_number = item[ "stock_number" ]

            if item[ "trading_date" ] != None:
                dict_per_trading_data[ TradingData.TRADING_DATE ] = item[ "trading_date" ]
            if item[ "trading_type" ] != None:
                if item[ "trading_type" ] == 0:
                    dict_per_trading_data[ TradingData.TRADING_TYPE ] = TradingType.BUY
                elif item[ "trading_type" ] == 1:
                    dict_per_trading_data[ TradingData.TRADING_TYPE ] = TradingType.SELL
            if item[ "trading_price" ] != None:
                dict_per_trading_data[ TradingData.TRADING_PRICE ] = float( item[ "trading_price" ] )
            if item[ "trading_count" ] != None:
                dict_per_trading_data[ TradingData.TRADING_COUNT ] = int( item[ "trading_count" ] )
            if item[ "trading_fee_discount" ] != None:
                dict_per_trading_data[ TradingData.TRADING_FEE_DISCOUNT ] = float( item[ "trading_fee_discount" ] )
            self.list_trading_data.append( dict_per_trading_data )
        
        sorted_list = sorted( self.list_trading_data, key=lambda x: ( datetime.datetime.strptime( x[ TradingData.TRADING_DATE ], "%Y-%m-%d"), x[ TradingData.TRADING_TYPE ] ) )
        self.refresh_table( sorted_list )

    def refresh_table( self, sorted_list ):
        self.per_stock_trading_data_model.clear()
        self.per_stock_trading_data_model.setVerticalHeaderLabels( ['交易日', '交易種類', '交易價格', '交易股數', '交易金額', '手續費', 
                                                                    '交易稅', '補充保費', '單筆總成本', '累計總成本', '庫存股數', '均價'] )
        self.ui.qtTradingDataTableView.horizontalHeader().hide()

        n_stock_inventory = 0
        n_accumulated_total_cost = 0

        for index, dict_per_trading_data in enumerate( sorted_list ):
            n_trading_type = dict_per_trading_data[ TradingData.TRADING_TYPE ]
            f_trading_price = dict_per_trading_data[ TradingData.TRADING_PRICE ]
            n_trading_count = dict_per_trading_data[ TradingData.TRADING_COUNT ]
            f_trading_fee_discount = dict_per_trading_data[ TradingData.TRADING_FEE_DISCOUNT ]
            dict_result = Computer.compute_cost( n_trading_type, f_trading_price, n_trading_count, f_trading_fee_discount, True, False )
            n_trading_value = dict_result[ TradingCost.TRADING_VALUE ]
            n_trading_fee = dict_result[ TradingCost.TRADING_FEE ]
            n_trading_tax = dict_result[ TradingCost.TRADING_TAX ]
            n_trading_insurance = dict_result[ TradingCost.TRADING_INSURANCE ]  
            n_per_trading_total_cost = dict_result[ TradingCost.TRADING_TOTAL_COST ]

            if n_trading_type == TradingType.BUY:
                n_stock_inventory += n_trading_count
                str_trading_type = "買進"
                n_accumulated_total_cost += n_per_trading_total_cost
            else:
                n_stock_inventory -= n_trading_count
                str_trading_type = "賣出"


            trading_date_item = QStandardItem( dict_per_trading_data[ TradingData.TRADING_DATE ] )
            trading_type_item = QStandardItem( str_trading_type )
            trading_price_item = QStandardItem( format( f_trading_price, "," ) )
            trading_count_item = QStandardItem( format( n_trading_count, "," ) )
            trading_value_item = QStandardItem( format( n_trading_value, "," ) )
            trading_fee_item = QStandardItem( format( n_trading_fee, "," ) )
            trading_tax_item = QStandardItem( format( n_trading_tax, "," ) )
            trading_insurance_item = QStandardItem( format( n_trading_insurance, "," ) )
            per_trading_total_cost_item = QStandardItem( format( n_per_trading_total_cost, "," ) )
            accumulated_total_cost_item = QStandardItem( format( n_accumulated_total_cost, "," ) )
            stock_inventory_item = QStandardItem( format( n_stock_inventory, "," ) )


            # condition_item = QStandardItem( str_value )
            # condition_item.setFlags( condition_item.flags() & ~Qt.ItemIsEditable )
            # condition_item.setTextAlignment( Qt.AlignHCenter | Qt.AlignVCenter )
            self.per_stock_trading_data_model.setItem( 0, index, trading_date_item ) # 交易日期
            self.per_stock_trading_data_model.setItem( 1, index, trading_type_item ) # 交易種類
            self.per_stock_trading_data_model.setItem( 2, index, trading_price_item ) # 交易價格
            self.per_stock_trading_data_model.setItem( 3, index, trading_count_item ) # 交易股數
            self.per_stock_trading_data_model.setItem( 4, index, trading_value_item ) # 交易金額
            self.per_stock_trading_data_model.setItem( 5, index, trading_fee_item ) # 手續費
            self.per_stock_trading_data_model.setItem( 6, index, trading_tax_item ) # 交易稅
            self.per_stock_trading_data_model.setItem( 7, index, trading_insurance_item ) # 補充保費
            self.per_stock_trading_data_model.setItem( 8, index, per_trading_total_cost_item ) # 單筆總成本
            self.per_stock_trading_data_model.setItem( 9, index, accumulated_total_cost_item ) # 累計總成本
            self.per_stock_trading_data_model.setItem( 10, index, stock_inventory_item ) # 庫存股數
            # self.per_stock_trading_data_model.setItem( 11, index, average_price_item ) # 均價
            pass

    def on_delete_data_push_button_clicked( self ):
        print("on_delete_data_push_button_clicked")

    def on_edit_data_push_button_clicked( self ):
        print("on_edit_data_push_button_clicked")
        # dialog = EditDialog()
        # dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)  # 創建應用程式
    app.setStyle('Fusion')
    window = MainWindow()  # 創建主窗口
    window.show()  # 顯示窗口
    sys.exit(app.exec())  # 進入事件循環