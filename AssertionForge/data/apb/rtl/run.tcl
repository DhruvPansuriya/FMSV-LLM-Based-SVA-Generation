set RTL_PATH .
clear -all
analyze -sv ${RTL_PATH}/apb_slave.v
analyze -sv ${RTL_PATH}/bindings.sva \
            ${RTL_PATH}/property_goldmine.sva
elaborate -top apb_slave
clock PCLK
reset -none
reset -expression {~PRESETn}
prove -all
