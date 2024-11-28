import { Paper } from "@mui/material";
import { styled } from "@mui/material/styles";
import { MessageType } from "./MessageType";

export const ChatText = styled(Paper)<{ messagetype: MessageType }>(
    ({ theme, messagetype: messageType }) => ({
      ...theme.typography.body2,
      padding: theme.spacing(1),
      marginTop: theme.spacing(1),
      color: theme.palette.text.secondary,
      borderRadius: "15px",
      borderTopLeftRadius: messageType === "ai" ? "2px" : undefined,
      borderTopRightRadius: messageType === "user" ? "2px" : undefined,
    })
  );
  
  
  