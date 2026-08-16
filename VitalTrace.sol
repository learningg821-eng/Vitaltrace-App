// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VitalTrace {

    struct VitalRecord {
        uint256 vitalId;
        uint256 patientId;
        string vitalHash;
        uint256 timestamp;
    }

    VitalRecord[] public records;

    event VitalRecorded(
        uint256 indexed vitalId,
        uint256 indexed patientId,
        string vitalHash,
        uint256 timestamp
    );

    function recordVital(
        uint256 _vitalId,
        uint256 _patientId,
        string memory _vitalHash
    ) public {
        records.push(
            VitalRecord({
                vitalId: _vitalId,
                patientId: _patientId,
                vitalHash: _vitalHash,
                timestamp: block.timestamp
            })
        );

        emit VitalRecorded(
            _vitalId,
            _patientId,
            _vitalHash,
            block.timestamp
        );
    }

    function getRecord(uint256 _index)
        public
        view
        returns (
            uint256 vitalId,
            uint256 patientId,
            string memory vitalHash,
            uint256 timestamp
        )
    {
        VitalRecord memory record = records[_index];

        return (
            record.vitalId,
            record.patientId,
            record.vitalHash,
            record.timestamp
        );
    }

    function getRecordCount() public view returns (uint256) {
        return records.length;
    }
}